#!/usr/bin/env python
import sys
import math
import lal, lalsimulation, lalburst

import numpy

from glue.ligolw import lsctables

def copy_sim_burst(row):
    """
    Turn a lsctables.SimBurst into a SWIG wrapped lalburst.SimBurst
    """

    swigrow = lalburst.CreateSimBurst()
    swigrow.hrss = row.hrss or 0
    time = lal.LIGOTimeGPS(row.time_geocent_gps, row.time_geocent_gps_ns)
    swigrow.time_geocent_gps = time
    swigrow.psi = row.psi
    swigrow.amplitude = row.amplitude or 0
    swigrow.egw_over_rsquared = row.egw_over_rsquared or 0
    swigrow.waveform_number = row.waveform_number or 0
    swigrow.pol_ellipse_angle = row.pol_ellipse_angle or 0.0
    swigrow.simulation_id = int(row.simulation_id)
    swigrow.q = row.q or 0.0
    swigrow.waveform = str(row.waveform)
    swigrow.bandwidth = row.bandwidth or 0.0
    swigrow.process_id = int(row.process_id)
    swigrow.frequency = row.frequency or 0.0
    swigrow.ra = row.ra
    swigrow.time_geocent_gmst = row.time_geocent_gmst or 0
    swigrow.pol_ellipse_e = row.pol_ellipse_e or 0.0
    swigrow.duration = row.duration or 0.0
    swigrow.dec = row.dec

    return swigrow

LAL_DETECTORS = dict(zip(
    [getattr(lal, name) for name in dir(lal) if name.endswith("DETECTOR_PREFIX")],
    [lal.CachedDetectors[d] for d in [getattr(lal, name) for name in dir(lal) if name.endswith("DETECTOR")]]
))

class SimBurstWaveform(lsctables.SimBurst):

    @classmethod
    def from_SimBurst(cls, sim_burst):
        sbw = SimBurstWaveform()
        for attr in dir(lsctables.SimBurst):
            if attr.startswith("__"):
                continue
            setattr(sbw, attr, getattr(sim_burst, attr))
        return sbw

    def __init__(self, *args, **kwargs):
        super(SimBurstWaveform, self).__init__(*args, **kwargs)
        self._fwdlen = 0
        self._fwdplan = None

    def time_series(self, sampling_rate, detector=None):
        """
        Generate a time series at a given sampling_rate (Hz) for the waveform using a call to lalsimulation. If detector is None (default), return only the (h+, hx) tuple. Otherwise, apply the proper detector anntenna patterns and return the resultant series F+h+ + Fxhx.
        """

        hp, hx = lalburst.GenerateSimBurst(copy_sim_burst(self), 1.0/sampling_rate)

        if detector is None:
            return hp, hx
    
        detector = LAL_DETECTORS[detector]
        return lalsimulation.SimDetectorStrainREAL8TimeSeries(hp, hx, self.ra, self.dec, self.psi, detector)

    def __get_fwdplan(self, sampling_rate, deltaF):
        fwdlen = int(sampling_rate/deltaF)
        if self._fwdplan is None or fwdlen != self._fwdlen:
            self._fwdplan = lal.CreateForwardREAL8FFTPlan(fwdlen, 1)
            self._fwdlen = int(sampling_rate/deltaF)

    def frequency_series(self, deltaF, detector=None, fwdplan=None):
        """
        Generate a frequency series at a given frequency bin spacing deltaF (Hz) for the waveform using a call to lalsimulation. The function time_series is called first to generate the waveform in the time domain. If detector is None (default), return only hf with no antenna patterns applied. Otherwise, apply the proper detector anntenna patterns and return the resultant series hf = FFT[F+h+ + Fxhx].
        """

        # FIXME: This is overkill for BTLWNB, and won't work entirely for 
        # cosmic strings
        sampling_rate = 4*(self.frequency + self.bandwidth or 0)
        sampling_rate = 2**(int(math.log(sampling_rate, 2)+1))
        self.__get_fwdplan(sampling_rate, deltaF)

        if detector is not None:
            h = self.time_series(sampling_rate, detector)
        else:
            hp, hx = self.time_series(sampling_rate, detector)
            h = lal.CreateREAL8TimeSeries(
                name = "TD signal",
                epoch = hp.epoch,
                f0 = 0,
                deltaT = hp.deltaT,
                sampleUnits = lal.DimensionlessUnit,
                length = hp.data.length
            )
            h.data.data = hp.data.data + hx.data.data
 
        # zero pad
        needed_samps = int(sampling_rate/deltaF)
        prevlen = h.data.length
        if h.data.length < needed_samps:
            h = lal.ResizeREAL8TimeSeries(h, 0, needed_samps)
        elif h.data.length > needed_samps:
            h = lal.ResizeREAL8TimeSeries(h, h.data.length-needed_samps, needed_samps)

        # adjust heterodyne frequency to match flow
        hf = lal.CreateCOMPLEX16FrequencySeries(
            name = "FD signal",
            epoch = h.epoch,
            f0 = 0,
            deltaF = deltaF,
            sampleUnits = lal.DimensionlessUnit,
            length = int(h.data.length/2 + 1)
        )

        # Forward FFT
        lal.REAL8TimeFreqFFT(hf, h, self._fwdplan)
        return hf

    def snr(self, psd=None, deltaF=0.125, detector=None):

        hf = self.frequency_series(deltaF, detector)

        # Assumed same deltaF and f0 = 0
        idx_lower, idx_upper = 0, min(len(hf.data.data), len(psd))

        hrss = (hf.data.data.conj() * hf.data.data)[idx_lower:idx_upper]
        if psd is None:
            return numpy.sqrt(hrss.sum()*hf.deltaF)

        # divide and sum for SNR
        nw_ip = numpy.nan_to_num(hrss / psd[idx_lower:idx_upper])
        power = 4 * numpy.real(sum(nw_ip)) * hf.deltaF
        return numpy.sqrt(power)

def read_snrs(fname):
    snrs = {}
    with open(fname) as fin:
        header = fin.readline()
        ifos = map(str.strip, fin.readline().split(" ")[2:])
        line = fin.readline()
        while line:
            line = line.split()
            snrs[line[0]] = dict(zip(ifos, map(float, line[1:])))
            line = fin.readline()
    return snrs

if __name__ == "__main__":
    from glue.ligolw import utils
    import sys
    xmldoc = utils.load_filename(sys.argv[1])
    sbt = lsctables.SimBurstTable.get_table(xmldoc)

    deltaF, fmax = 0.125, 4096.0
    psd_len = fmax/deltaF
    psd = map(lalsimulation.SimNoisePSDaLIGOZeroDetHighPower, 
        numpy.linspace(0, psd_len, psd_len+1)*deltaF)

    ifos = ("H1", "L1", "V1")

    with open("H1L1V1_snrs.txt", "w") as fout:
        #
        # Write header
        #
        print >>fout, "# deltaF %e flow %e fhigh %e" % (deltaF, 0.0, fmax)
        print >>fout, "# simulation_id H1 L1 V1"

        for sim in sbt:
            sbw = SimBurstWaveform.from_SimBurst(sim)
            fout.write(str(sim.simulation_id) + " ")
            print >>fout, " ".join("%e" % sbw.snr(psd, detector = ifo) for ifo in ifos)

    #snrs = read_snrs("H1L1V1_snrs.txt")
    #print snrs.values()
