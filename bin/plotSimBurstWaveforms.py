#!/usr/bin/env python
#
# Copyright (C) 2013 Sydney J. Chamberlin 
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

import sys, os, string
import numpy as np
from matplotlib import pyplot as plt

import lal
import lalmetaio
import lalburst
import lalsimulation

from optparse import OptionParser
## define option parsers
optp = OptionParser()
optp.add_option("--nyquist-frequency", type=float, default=16., help="Nyquist frequency of the PSD to generate. Default is 16 Hz.")
optp.add_option("--hrss-det", action='store_true', help="If option is specified, will compute hrss_detector instead of hrss.")

opts, args = optp.parse_args()

#
# Import sim_burst table as linked list from lalburst
#
sim_burst_table = lalburst.SimBurstTableFromLIGOLw(sys.argv[1], None, None)

#
# Obtain various waveform parameters from sim burst table
#
from collections import defaultdict
waveforms = defaultdict(list)
while True:
	waveforms[sim_burst_table.waveform].append(sim_burst_table)
	if sim_burst_table.next is None: break
	sim_burst_table = sim_burst_table.next

print 'obtaining simBurst table... '
# I can can generalize 
if len(waveforms) <= 1:
	raise InputError('Input expected to contain sim_burst table with both white noise bursts and sine gaussians')

#
## Sampling parameters
#

# nyquist frequency is determined by DATA. preferably a power of 2.
if opts.nyquist_frequency is not None:
	fnyq = opts.nyquist_frequency
else:
	fnyq = 16.

deltaT = 1./(2.*fnyq)

#
## Use lalburst to generate hp, hx for specified waveforms.
#

# note index selects a single row from the simBurst table
wnb_hp, wnb_hx = lalburst.GenerateSimBurst(waveforms["BTLWNB"][1], deltaT)
sg_hp, sg_hx = lalburst.GenerateSimBurst(waveforms["SineGaussian"][0], deltaT)

#if opts.waveform_length == None:
#	deltaF = 1./waveforms["BTLWNB"][1].duration
#	print 'deltaF = ', deltaF
#else:
#	deltaF = 1./waveform_length

#
## Establish the hrss
#

# define detectors in swigland notation
det = lal.lalCachedDetectors[lal.LAL_LHO_4K_DETECTOR]

# want strain time series for each detector -- calculate using hp, hx for each type of waveform

psd = 1.0 # as we decided...

wnb_deltaF = 1./(wnb_hp.data.length)
sg_deltaF = 1./(sg_hp.data.length)
#	print wn_deltaF, sg_deltaF

# gonna manually choose deltaF to be related to a power of 2, we can change this later
deltaF = 1./128

print "check choice of deltaF, might need to adjust:"
print wnb_deltaF, sg_deltaF, deltaF

# our fft will be easier if we zero pad (or truncate if we have too much)

needed_samps = int(2.0*fnyq/deltaF) # to have enough resolution

if opts.hrss_det is not True:
	
	# compute h(t) = h+(t) + hx(t)
	h_wnb = wnb_hp.data.data + wnb_hx.data.data
	h_sg = sg_hp.data.data + sg_hx.data.data
	
	# make lal time series to set numpy arrays equal to
	lal_h_wnb = lal.CreateREAL8TimeSeries(name = "lal_wnb", epoch = wnb_hp.epoch, f0=0, deltaT = deltaT, sampleUnits = lal.lalDimensionlessUnit, length = len(wnb_hp.data.data+wnb_hx.data.data))
	lal_h_sg = lal.CreateREAL8TimeSeries(name = "lal_sg", epoch = sg_hp.epoch, f0=0, deltaT =deltaT, sampleUnits = lal.lalDimensionlessUnit, length = len(sg_hp.data.data+sg_hx.data.data))
	
	#h_wnb = lal_h_wnb
	h_wnb = lal_h_wnb
	h_sg = lal_h_sg

else:
	
	# use lal version of h: h(t) = F+ h+(t) + Fx hx(t) 
	h_wnb = lalsimulation.SimDetectorStrainREAL8TimeSeries( wnb_hp, wnb_hx, sim_burst_table.ra, sim_burst_table.dec, sim_burst_table.psi, det )
	h_sg = lalsimulation.SimDetectorStrainREAL8TimeSeries( sg_hp, sg_hx, sim_burst_table.ra, sim_burst_table.dec, sim_burst_table.psi, det )

# resize if necessary for FFT
if h_wnb.data.length < needed_samps:
	h_wnb = lal.ResizeREAL8TimeSeries( h_wnb, 0, needed_samps )
elif h_wnb.data.length > needed_samps:
	h_wnb = lal.ResizeREAL8TimeSeries( h_wnb, h_wnb.data.length-needed_samps, needed_samps )

if h_sg.data.length < needed_samps:
	h_sg = lal.ResizeREAL8TimeSeries( h_sg, 0, needed_samps )
elif h_sg.data.length > needed_samps:
	h_sg = lal.ResizeREAL8TimeSeries( h_sg, h_sg.data.length-needed_samps, needed_samps )

hf_wnb = lal.CreateCOMPLEX16FrequencySeries(
									name = "m1",
									epoch = h_wnb.epoch,
									f0 = 0,
									deltaF = deltaF,
									sampleUnits = lal.lalDimensionlessUnit,
									length = h_wnb.data.length/2 + 1
									)

hf_sg = lal.CreateCOMPLEX16FrequencySeries(
										name = "n1",
										epoch = h_sg.epoch,
										f0 = 0,
										deltaF = deltaF,
										sampleUnits = lal.lalDimensionlessUnit,
										length = h_sg.data.length/2 + 1
										)

fwdlen = needed_samps

wnb_fwdplan = lal.CreateForwardREAL8FFTPlan( h_wnb.data.length, fwdlen )
sg_fwdplan = lal.CreateForwardREAL8FFTPlan( h_sg.data.length, fwdlen )

#perform FFTs
print 'performing FFTs... '
lal.REAL8TimeFreqFFT( hf_wnb, h_wnb, wnb_fwdplan )

lal.REAL8TimeFreqFFT( hf_sg, h_sg, sg_fwdplan )

# now can compute hrss. normally would account for psd in power but since it's set to 1 this is trivial
# FIX ME check factor of 2, might actually be factor of 4
wnb_hrss = hf_wnb.data.data.conj() * hf_wnb.data.data
wnb_power = 2 * np.real(sum(wnb_hrss)) * hf_wnb.deltaF

sg_hrss = hf_sg.data.data.conj() * hf_sg.data.data
sg_power = 2 * np.real(sum(sg_hrss)) * hf_sg.deltaF

#
## Generate Plots
#

## duration of signal (WLOG chose hp, should be identical for hx) for plots
# white noise bursts
wnb_dur = len(wnb_hp.data.data)*wnb_hp.deltaT
wnb_time_range = np.arange(0., wnb_dur,wnb_hp.deltaT)
wnb_freq_range = np.arange(0.,fnyq,fnyq/len(wnb_hrss))

# sine gaussians
sg_dur = len(sg_hp.data.data)*sg_hp.deltaT
sg_time_range = np.arange(0., sg_dur, sg_hp.deltaT)
sg_freq_range = np.arange(0.,fnyq,fnyq/len(sg_hrss))

## psd plots (with calcualted hrss)
fig0 = plt.figure(0)

plt.subplot(211)
plt.plot(wnb_freq_range, np.real(wnb_hrss))
plt.xlabel("Freq (Hz)")
plt.ylabel("BTLWNB psd")

plt.subplot(212)
plt.plot(sg_freq_range, np.real(sg_hrss))
plt.xlabel("Freq (Hz)")
plt.ylabel("sine Gaussian psd")

## times series of waveforms
fig1 = plt.figure(1)

np.savetxt("wnb_Timedata_from_python.txt",wnb_time_range)
np.savetxt("wnb_data_from_python.txt",wnb_hp.data.data)

plt.subplot(211)
plt.plot(wnb_time_range, wnb_hp.data.data,label='plus')
plt.plot(wnb_time_range, wnb_hx.data.data, label='cross')
plt.xlabel("Time (s)")
plt.ylabel("Strain, $h_{+}$ and $h_x$")
#plt.title("Time series of injection waveforms (utilized via lalsimulation)", fontsize=14, fontweight='bold')
plt.legend(loc='upper right')

plt.subplot(212)
plt.plot(sg_time_range, sg_hp.data.data,label='plus')
plt.plot(sg_time_range, sg_hx.data.data, label='cross')
plt.xlabel("Time (s)")
plt.ylabel("Strain, $h_{+}$ and $h_x$")
plt.legend(loc='upper right')

## injection parameter distribution plots

# use dict structure to access parameters from sim burst table 
waveform_types = waveforms.keys()
wnb_frequency_parameters = [sb.frequency for sb in waveforms["BTLWNB"]]
sg_frequency_parameters = [sb.frequency for sb in waveforms["SineGaussian"]]
q_numbers = [sb.q for sb in waveforms["SineGaussian"]]
duration_parameters = [sb.duration for sb in waveforms["BTLWNB"]]
bandwidth_parameters = [sb.bandwidth for sb in waveforms["BTLWNB"]]

print "wn and sg frequencies", wnb_frequency_parameters[1], sg_frequency_parameters[0]
print "q", q_numbers[0]
print "dur", duration_parameters[1]
print "band", bandwidth_parameters[1]

fig2 = plt.figure(2)

plt.subplot(211)
plt.scatter(duration_parameters,bandwidth_parameters)
plt.xlabel("Duration (s)")
plt.ylabel("Bandwidth (Hz) ")
plt.title("BTLWNB injection waveform parameter distributions", fontsize=14)

plt.subplot(212)
plt.scatter(sg_frequency_parameters,q_numbers)
plt.xlabel("Frequencies (Hz)")
plt.ylabel("Sine Gaussian Q number ")
plt.title("Sine Gaussian injection waveform parameter distributions", fontsize=14)

plt.tight_layout()
plt.show()
