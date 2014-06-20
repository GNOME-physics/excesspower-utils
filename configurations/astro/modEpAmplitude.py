# Copyright (C) 2014 Sydney J. Chamberlinn
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#

import numpy
from glue.ligolw import table, lsctables, utils
import sys, glue
from collections import defaultdict
from gstlal import reference_psd

#
# =============================================================================
#
#                                  Definitions
#
# =============================================================================
#

# amplitude definitions
def new_compute_amplitude( sb, psd ):
        """
        Replaced <S> with 1/<1/S> in hrss def'n. Use snr_r = E/d-1
        """
        flow = int((sb.central_freq - sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        fhigh = int((sb.central_freq + sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        sb.amplitude = numpy.sqrt(  1./2. * sb.snr / ( ( 1/psd.data[flow:fhigh]*psd.deltaF ).sum() / sb.bandwidth ) )

def tile_energy_E_new_compute_amplitude( sb, psd):
        """
        Replaced <S> with 1/<1/S> in hrss def'n. Use snr = E
        """
        flow = int((sb.central_freq - sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        fhigh = int((sb.central_freq + sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        ndof = sb.duration*sb.bandwidth*2.
        snr = (sb.snr+1.)*ndof
        sb.amplitude = numpy.sqrt(  1./2. * snr / ( ( 1/psd.data[flow:fhigh]*psd.deltaF ).sum() / sb.bandwidth ) )

def tile_energy_Eminusd_new_compute_amplitude( sb, psd):
        """
        Replaced <S> with 1/<1/S> in hrss def'n. Use snr = E
        """
        flow = int((sb.central_freq - sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        fhigh = int((sb.central_freq + sb.bandwidth/2.0 - psd.f0)/psd.deltaF)
        ndof = sb.duration*sb.bandwidth*2.
        snr = (sb.snr+1.)*ndof
        sb.amplitude = numpy.sqrt(  1./2. * snr / ( ( 1/psd.data[flow:fhigh]*psd.deltaF ).sum() / sb.bandwidth ) )

#
# =============================================================================
#
#                                 Command Line
#
# =============================================================================
#

from optparse import OptionParser
optp = OptionParser()
optp.add_option("--det-psd-file", action = 'store', type = 'string', help="Specify path to xml file containing psd. Required.")
optp.add_option("--triggers", action='store', type = 'string', help="Specify path to xml file containing unclustered triggers. Required.")

opts, args = optp.parse_args()

# load psd 
psdxml = utils.load_filename('L1_PSD_measured.xml.gz')
measuredpsd = reference_psd.read_psd_xmldoc(psdxml)
measuredpsd = measuredpsd['L1']

# load original unclustered triggers
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
num_rows = len(sngl_burst)
#
# =============================================================================
#
#                            Original clustering method
#
# =============================================================================
#

# new
print 'making new hrss files...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	float(idx), float(num_rows)
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
	new_compute_amplitude( row, measuredpsd)

utils.write_filename(xmldoc, 'unc_new.xml.gz', gz = True)
sys.exit()
#tile energy E new
print '\n making tile_energy_E new hrss files...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
	tile_energy_E_new_compute_amplitude( row, measuredpsd)

utils.write_filename(xmldoc, 'unc_E_new.xml.gz', gz = True)

# tile energy E-d new
print '\n making tile_energy_E-d new hrss with root snr...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
        tile_energy_Eminusd_new_compute_amplitude( row, measuredpsd)

utils.write_filename(xmldoc, 'unc_E-d_new.xml.gz', gz = True)

#
# =============================================================================
#
#                              New clustering method
#
# =============================================================================
#

# new 
print '\n making new hrss with root snr...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
	new_compute_amplitude( row, measuredpsd)
	row.snr = (row.snr)**.5

utils.write_filename(xmldoc, 'unc_root_new.xml.gz', gz = True)

# tile energy E new
print '\n making tile_energy_E new hrss with root snr...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
        tile_energy_E_new_compute_amplitude( row, measuredpsd)
        row.snr = (row.snr)**.5

utils.write_filename(xmldoc, 'unc_root_E_new.xml.gz', gz = True)

# tile energy E-d new
print '\n making tile_energy_E-d new hrss with root snr...'
xmldoc = utils.load_filename('unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz')
sngl_burst = table.get_table(xmldoc, lsctables.SnglBurstTable.tableName)
for idx, row in enumerate(sngl_burst):
	sys.stdout.write( "\r Processing %d / %d " % (idx, num_rows)  )
        tile_energy_Eminusd_new_compute_amplitude( row, measuredpsd)
	row.snr = (row.snr)**.5

utils.write_filename(xmldoc, 'unc_root_E-d_new.xml.gz', gz = True)

print 'done.'
