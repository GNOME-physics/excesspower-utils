import sys
import os
import itertools
from collections import OrderedDict
import subprocess
import shlex
from xml.etree import ElementTree
from ConfigParser import ConfigParser

from glue.pipeline import CondorJob

ONLINE_INCANTATION = {"+Online_Burst_ExcessPower": "True",
    "Requirements": "(Online_Burst_ExcessPower =?= True)" 
}

# NOTE: pipeline classes are old-style. ...really?
class EPOnlineCondorJob(CondorJob, object):
    """
    Class representing a type of condor job corresponding to an online (never-ending) gstlal_excesspower job.
    """
    @classmethod
    def from_config_section(cls, cfgp, sec, rootdir):
        """
        Create an instance from a section in a subsystem configuration file.
        """
        chan_cfg_file = cfgp.get(sec, "configuration_file")
        manager = EPOnlineCondorJob(sec, chan_cfg_file, rootdir)

        sample_rate = cfgp.getint(sec, "sample_rate")
        if cfgp.has_option(sec, "downsample_rate"):
            ds_rate = cfgp.getint(sec, "downsample_rate")
        else:
            ds_rate = None
        manager.set_sample_rate(sample_rate, ds_rate)

        odc_chan, on_bits, off_bits = None, None, None
        if cfgp.has_option(sec, "dq_channel"):
            odc_chan = cfgp.get(sec, "dq_channel")
        if cfgp.has_option(sec, "on_bits"):
            if cfgp.get(sec, "on_bits"):
                on_bits = int(cfgp.get(sec, "on_bits"), 16)
            else:
                on_bits = None
        if cfgp.has_option(sec, "off_bits"):
            if cfgp.get(sec, "off_bits"):
                off_bits = int(cfgp.get(sec, "off_bits"), 16)
            else:
                off_bits = None
        manager.set_dq_channel(odc_chan, on_bits, off_bits)
        return manager

    def __init__(self, channel, configuration_file, rootdir):
        super(EPOnlineCondorJob, self).__init__(universe="vanilla", executable="./gstlal_excesspower", queue=1)

        self.instrument, self.channel = channel.split(":")
        self.subsys = self.channel.split("-")[0]

        self.root_dir = rootdir

        self.set_config_file(configuration_file)

        # Number of cores to request for this job
        self.ncpu = 1

        # Amount of memory to request
        self.mem_req = 1024

        # Online running requires us to identify the resource which
        # won't evict us 
        for incant, val in ONLINE_INCANTATION.iteritems():
            self.add_condor_cmd(incant, val)

        # Since gstreamer doesn't always tell us what's wrong, we'll
        # enable basic error reporting
        self.add_condor_cmd("environment", "GST_DEBUG=2")

        # Things which are nice to have
        self.add_condor_cmd("want_graceful_removal", "True")
        self.add_condor_cmd("kill_sig", "15")

        #
        # Things that are likely to be true for this
        #

        # channel specification
        self.add_opt("channel-name", "%s=%s" % (self.instrument, self.channel))
        
        # data source: We read from the GDS created shared memory partition
        self.add_opt("data-source", "lvshm")

        # Enable some basic statistical monitoring
        self.add_arg("enable-channel-monitoring")

        # Please be verbose, thank you!
        self.add_arg("verbose")

        # Things that are off by default
        self.dq_channel = None
        self.on_bits, self.off_bits = None, None
        self.shm_part_name = None

        self.sample_rate, self.downsample_rate = None, None

        self.out_log_path = None
        self.err_log_path = None
        self.log_path = None
        self.iwd = None

    def status(self, attrs=None):
        return OrderedDict([ (k, getattr(self, k) or "") for k in ['instrument', 'subsys', 'channel', "sample_rate", "downsample_rate", 'configuration_file', 'dq_channel', 'off_bits', 'on_bits', 'shm_part_name']])

    def condor_status(self, attrs=None):
        return OrderedDict([ (k, getattr(self, k)) for k in ['ncpu', 'mem_req', 'root_dir', 'iwd', 'log_path', 'err_log_path', 'out_log_path']])

    def full_name(self):
        """
        Get the 'fully qualified' name of the channel.
        """
        return "%s:%s" % (self.instrument, self.channel)

    # Utility to allow the class to call the underlying configuration object
    # so we can query things about it if we want
    def get_config_attr(self, attr):
        for sec in self.cfg.sections():
            if self.cfg.has_option(sec, attr.replace("_", "-")):
                return self.cfg.get(sec, attr.replace("_", "-"))
        raise AttributeError(attr)

    def set_config_attr(self, attr, val):
        for sec in self.cfg.sections():
            if self.cfg.has_option(sec, attr.replace("_", "-")):
                self.cfg.set(sec, attr.replace("_", "-"), val)
                return
        setattr(self, attr, val)

    def set_sample_rate(self, rate, downsample_rate=None):
        """
        Since the sample rate controls much about what the process will do and some of the default options, it has its own setter so that it can reconfigure as appropriate.
        """

        if rate > 2048:
            self.ncpu = 2
            self.mem_req = 2048
        else:
            self.ncpu = 1
            self.mem_req = 1024

        self.sample_rate = rate
        if downsample_rate is not None:
            self.add_opt("sample-rate", downsample_rate)
            self.downsample_rate = downsample_rate

        self.add_condor_cmd("request_cpu", str(self.ncpu))
        self.add_condor_cmd("request_memory", str(self.mem_req))

    def cluster(self):
        """
        Enable clustering. WARNING: Currently, once you've set this, there's no going back. You have to make a new instance of the class to reset it.
        """
        self.add_arg("clustering")
        # FIXME: This should be a toggle, so we need to test:
        # del self.__options["clustering"]

    def do_getenv(self):
        """
        Pull in user environment. Useful for running EP from non-system releases.
        """
        self.add_condor_cmd("getenv", "True")
        # FIXME: This should be a toggle, so we need to test:
        # del self.__condor_cmds["getenv"]

    def set_dq_channel(self, dq_channel=None, on_bits=0x1, off_bits=0x0):
        """
        Set the data quality (usually ODC) channel for this channel. Optionally set on bits (default 0x1) and off bits (default 0x0, e.g. ignore).
        """
        if dq_channel is None:
            return # noop
        self.dq_channel = dq_channel
        self.on_bits, self.off_bits = on_bits, off_bits
        self.add_opt("dq-channel", "%s=%s" % (self.instrument, self.dq_channel))
        if self.on_bits is not None:
            self.add_opt("state-vector-on-bits", "%x" % self.on_bits)
        if self.off_bits is not None:
            self.add_opt("state-vector-off-bits", "%x" % self.off_bits)

    def set_shm_partition(self, shm_part_name):
        """
        Set the name of the shared memory partition from which to draw data. Check with smlist command line utility, usually something like LHO_Data or LLO_Data.
        """
        self.shn_part_name = shm_part_name
        self.add_opt("shared-memory-partition", "%s=%s" (self.instrument, self.shm_part_name))

    def set_config_file(self, config_path):
        """
        Set the instance configuration file path. This will both set it in the condor job as well as make the attributes available through this instance.
        """
        self.configuration_file = config_path
        if self.configuration_file:
            self.cfg = ConfigParser()
            self.cfg.read(self.configuration_file)
        else:
            self.cfg = None
        self.add_opt("initialization-file", self.configuration_file)

    def write_config_file(self, out_path):
        """
        Write out configuration file for this instance of EP. If out_path is a writable stream, write out config file, but do not change internal path.
        """
        if hasattr(out_path, "write"):
            self.cfg.write(out_path)
            return

        with open(out_path, "w") as fout:
            self.cfg.write(fout)
        self.configuration_file = out_path

    def set_root_directory(self, path):
        """
        Set the root directory from which to stage this job.
        """
        self.root_dir = path

    def get_wd(self):
        """
        Get the base directory for this job.
        """
        return os.path.join(os.path.abspath(self.root_dir), self.instrument, self.subsys, self.channel)

    def finalize(self):
        """
        Create directory structure, and write out relevant files.
        """

        self.iwd = self.get_wd()
        self.add_condor_cmd("iwd", self.iwd)
        if not os.path.exists(self.iwd):
            os.makedirs(self.iwd)

        log_path = os.path.join(self.iwd, "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        self.out_log_path = os.path.join(log_path, "%s_%s_output-$(Cluster).out" % (self.instrument, self.channel))
        self.set_stdout_file(self.out_log_path)
        self.err_log_path = os.path.join(log_path, "%s_%s_error-$(Cluster).err" % (self.instrument, self.channel))
        self.set_stderr_file(self.err_log_path)
        self.log_path = os.path.join(log_path, "%s_%s_log-$(Cluster).log" % (self.instrument, self.channel))
        self.set_log_file(self.log_path)

        cfg_file = os.path.join(self.iwd, "%s_%s_config.ini" % (self.instrument, self.channel))
        self.write_config_file(cfg_file)
        # Reset the path so the submit file knows where to go
        self.set_config_file(cfg_file)

        self.sub_file = os.path.join(self.iwd, "%s_%s_submit.sub" % (self.instrument, self.channel))
        self.set_sub_file(self.sub_file)
        self.write_sub_file()

def write_all_configs(managers, working_dir="./", append=True):
    def categorize(mngr):
        return (mngr.instrument, mngr.subsys)

    written_configs = []
    for (inst, subsys), mlist in itertools.groupby(sorted(managers, key=EPOnlineCondorJob.full_name), categorize):
        inst_dir = os.path.join(working_dir, inst)
        if not os.path.exists(inst_dir):
            os.makedirs(inst_dir)
        cfg_fname = os.path.join(inst_dir, "%s_channels.ini" % subsys.lower())
        write_subsystem_config(mlist, cfg_fname, append)
        written_configs.append(cfg_fname)

    return written_configs
            

def write_subsystem_config(managers, path, append=True):
    cfgp = ConfigParser()
    if append:
        with open(path, "r") as cfgf:
            cfgp.read(cfgf)
    for mngr in managers:
        sec = mngr.full_name()
        cfgp.add_section(sec)
        #for a in ["instrument", "sample_rate", "configuration_file", "dq_channel", "on_bits", "off_bits", "priority"]:
        for a in ["instrument", "sample_rate", "configuration_file", "dq_channel", "on_bits", "off_bits"]:
            val = getattr(mngr, a)
            cfgp.set(sec, a, "" if val is None else val)

    if hasattr(path, "write"):
        cfgp.write(path)
        return

    with open(path, "w") as fout:
        cfgp.write(fout)

def submit_condor_job(job):
    cmd = shlex.split("/usr/bin/condor_submit %s" % job.sub_file)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    # FIXME: This would be so much easier if condor did anything but
    # print to the screen
    cpid = -1
    if proc.returncode == 0:
        cpid = int(out.split("\n")[1].split()[-1][:-1])
        pidfile = os.path.join(job.iwd, "condor.pid")
        with open(pidfile, "w") as pidf:
            print >>pidf, cpid
    else:
        print >>sys.stderr, "Failed to submit condor job (got status %d). Stderr follows:\n%s" % (proc.returncode, err)

    return proc.returncode, cpid

def kill_condor_job(job, pid=None):
    if pid is None:
        pidf = os.path.join(job.get_wd(), "condor.pid")
        if not os.path.exists(pidf):
            raise IOError("No condor PID lockfile exists.")
        else:
            with open(pidf) as f:
                pid = int(f.read())

    cmd = shlex.split("/usr/bin/condor_rm %s" % pid)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    # FIXME: This would be so much easier if condor did anything but
    # print to the screen
    if proc.returncode != 0:
        print >>sys.stderr, "Failed to kill condor job (got status %d). Stderr follows:\n%s" % (proc.returncode, err)
    else:
        os.unlink(pidf)

    return proc.returncode

def parse_condor_xml_node(node):
    job_stat = {}
    for attr in node:
        job_stat[attr.attrib["n"]] = attr[0].text if attr[0].text != '' else attr[0].attrib["b"]
    return job_stat

def get_condor_status(user=None):
    cmd = shlex.split("/usr/bin/condor_q -xml %s" % os.environ["USER"])
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    xml = proc.communicate()[0]
    
    root = ElementTree.fromstring(xml)
    jobs = []
    for job in root:
        jobs.append(parse_condor_xml_node(job))

    return jobs
