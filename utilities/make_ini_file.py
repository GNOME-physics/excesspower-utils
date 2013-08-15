#!/usr/bin/env python

import sys

entry = """
[%(channel)s]
instrument=%(inst)s
sample_rate=%(rate)s
ini_file=%(ini)s
odc_channel=%(odc)s
on_bits=%(on_bits)s
off_bits=%(off_bits)s
"""

def infer_odc(chan, odc_channels):
	"""
	Figure out the best matching ODC channel for a given input channel.
	"""
	if len(odc_channels) == 0:
		return None
	tmp_odc = [ odc.replace("-", "_") for odc in odc_channels ]
	odcs = [ (compare_odc(chan.replace("-", "_"), odc), odc) for odc in tmp_odc ]
	# FIXME: What happens if the top rank is duplicated
	winner = sorted( odcs )[-1][1].split("_")
	return winner[0] + "-" + "_".join(winner[1:])

def compare_odc(chan, odc):
	"""
	Find longest match of chan and odc. Return length of match.
	"""
	subchans = chan.split("_")
	subodcs = odc.split("_")
	minlen = min(len(subchans), len(subodcs))
	while subchans[:minlen] != subodcs[:minlen]:
		minlen -= 1
	return minlen

if len(sys.argv) == 1:
	lines = sys.stdin.readlines()
else:
	lines = open(sys.argv[1]).readlines()

# preprocess for odc
odc_channels = []
for line in lines:
	chan, rate = line.split()
	det, chan = chan.split(":")
	sub, schan = chan.split("-")
	if "ODC_CHANNEL" in chan:
		odc_channels.append( chan )

for line in lines:
	chan, rate = line.split()
	det, chan = chan.split(":")
	sub, schan = chan.split("-")

	if "ODC_CHANNEL" in schan:
		print >>sys.stderr, "Skipping ODC channel: %s." % chan
		continue

	odc_chan = infer_odc(chan, odc_channels)
	inifile = "/home/detchar/excesspower/%s/channel_ini/gstlal_excesspower_%s_%s_%s.ini" % (det, det.lower(), sub.lower(), rate)
	print entry % {"channel": chan, "rate": rate, "inst": det, "ini": inifile, "odc": odc_chan or "", "on_bits": "0x1", "off_bits": "0x0" }
