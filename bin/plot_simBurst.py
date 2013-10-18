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


import sys
import numpy as np
from matplotlib import pyplot as plt

import lalmetaio
import lalburst
import lalsimulation

#
# Import sim_burst table
#
sim_burst_table = lalburst.SimBurstTableFromLIGOLw(sys.argv[1], None, None)

#
# Obtain various waveform parameters from sim burst table
#
sim_table_rows = []
while True:
	sim_table_rows.append([sim_burst_table.waveform,sim_burst_table.frequency,sim_burst_table.q,sim_burst_table.duration,sim_burst_table.bandwidth])
	if sim_burst_table.next is None: break
	sim_burst_table = sim_burst_table.next

waveform_types = [sim_table_rows[jj][0] for jj in range(len(sim_table_rows))]
frequency_parameters = [sim_table_rows[jj][1] for jj in range(len(sim_table_rows))]
q_parameters = [sim_table_rows[jj][2] for jj in range(len(sim_table_rows))]
duration_parameters = [sim_table_rows[jj][3] for jj in range(len(sim_table_rows))]
bandwidth_parameters = [sim_table_rows[jj][4] for jj in range(len(sim_table_rows))]

#
# Use lalburst to generate hp, hx for specified waveforms (use .next to iterate to intended sim burst row)
# for some reason (related to swig bindings?) you will get a seg fault 11 if you try to use the already-defined sim_burst_table as the argument to GenerateSimBurst. This hack seems to get us around that problem, for now... 
#
wnb_hp, wnb_hx = lalburst.GenerateSimBurst(lalburst.SimBurstTableFromLIGOLw('mixed_low_freq.xml', None, None), 1.0/16384)
sg_hp, sg_hx = lalburst.GenerateSimBurst(lalburst.SimBurstTableFromLIGOLw('mixed_low_freq.xml', None, None).next, 1.0/16384)

#
## duration of signal (WLOG chose hp, should be identical for hx)
#
wnb_dur = len(wnb_hp.data.data)*wnb_hp.deltaT
wnb_time_range = np.arange(0., wnb_dur, wnb_hp.deltaT)

sg_dur = len(sg_hp.data.data)*sg_hp.deltaT
sg_time_range = np.arange(0., sg_dur, sg_hp.deltaT)

#
## Plot waveforms (time series) 
#
fig1 = plt.figure(1)

plt.subplot(211)
plt.plot(wnb_time_range, wnb_hp.data.data,label='plus')
plt.plot(wnb_time_range, wnb_hx.data.data, label='cross')
plt.xlabel("Time (s)")
plt.ylabel("Strain, $h_{+}$ and $h_x$")
#plt.suptitle("Injection waveforms plotted with lalsimulation", fontsize=14, fontweight='bold')
plt.title("BTLWNB or Sine Gaussian injection waveforms plotted with lalsimulation", fontsize=14, fontweight='bold')
plt.legend(loc='upper right')

plt.subplot(212)
plt.plot(sg_time_range, sg_hp.data.data,label='plus')
plt.plot(sg_time_range, sg_hx.data.data, label='cross')
plt.xlabel("Time (s)")
plt.ylabel("Strain, $h_{+}$ and $h_x$")
plt.legend(loc='upper right')

plt.show()

# plot parameter distributions

fig2 = plt.figure(2)

plt.subplot(211)
plt.scatter(frequency_parameters,q_parameters)
plt.xlabel("Frequencies (Hz)")
plt.ylabel("Sine Gaussian Q number ")
plt.title("Sine Gaussian injection waveform parameters", fontsize=14, fontweight='bold')
#
plt.subplot(212)
plt.scatter(duration_parameters,bandwidth_parameters)
plt.xlabel("Duration (s)")
plt.title("BTLWNB injection waveform parameters", fontsize=14, fontweight='bold')
plt.ylabel("Bandwidth (Hz) ")

plt.show()
