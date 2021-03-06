#/bin/bash

burst_stuff="# q bandwidth waveform\n
3.0 0.1 BTLWNB\n
15.0 1.0 SineGaussian"

insp_stuff="# inclination waveform distance geocent_end_time geocent_end_time_ns mass1 mass2\n
1.34 SpinTaylorT4 1000 1000000000 0 1.4 10.0\n
0.45 EOBNRv2HM 2300 1000000000 100000 5.0 5.0"

echo $burst_stuff > sb_test.dat
echo $insp_stuff > si_test.dat

./ligolw_encode --parse-burst sb_test.dat --parse-inspiral si_test.dat --fill-in-values --output-file inj_test.xml.gz
ligolw_print -t sim_burst -t sim_inspiral inj_test.xml.gz
