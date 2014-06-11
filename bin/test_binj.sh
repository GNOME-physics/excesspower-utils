#!/bin/bash

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 10000 \
    --output mixed_test.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type random  \
    --event-rate 1e6  \
    --burst-family BTLWNB \
    --wnb-max-dist 1   \
    --wnb-min-egw 1e-5 \
    --wnb-max-egw 1e-3 \
    --wnb-min-bandwidth 10 \
    --wnb-max-bandwidth 100 \
    --wnb-min-duration 1e-2 \
    --wnb-max-duration 1e-1 \
    --wnb-min-frequency 10 \
    --wnb-max-frequency 1000  \
    --burst-family SineGaussian \
    --sg-polarization-type elliptical \
    --sg-fix-hrss 2e-24 \
    --sg-fix-hrss 1e-25 \
    --sg-fix-hrss 5e-23 \
    --sg-fix-hrss 1e-23 \
    --sg-fix-q 10 \
    --sg-fix-q 100 \
    --sg-fix-q 3 \
    --sg-fix-f 200 \
    --sg-fix-f 500 \
    --sg-fix-f 1000 \
    --write-mdc-log test.log 

exit
./ligolw_inj_snr --det-psd-func H1=SimNoisePSDaLIGOZeroDetHighPower --det-psd-func L1=SimNoisePSDaLIGOZeroDetHighPower --det-psd-func V1=SimNoisePSDaLIGOZeroDetHighPower mixed_test.xml
exit

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 1000 \
    --output impulse_test.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type fixed  \
    --event-rate 1e6  \
    --burst-family Impulse \
    --imp-fix-hrss 2e-24 \
    --imp-fix-hrss 1e-25 \
    --imp-fix-hrss 5e-23 \
    --imp-fix-hrss 1e-23
exit

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 1000 \
    --burst-family SineGaussian \
    --output sg_test.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type fixed  \
    --jitter 1.5 \
    --event-rate 1e5  \
    --sg-polarization-type elliptical \
    --sg-fix-hrss 2e-23 \
    --sg-fix-hrss 1e-21 \
    --sg-fix-hrss 5e-19 \
    --sg-fix-q 10 \
    --sg-fix-q 100 \
    --sg-fix-q 3 \
    --sg-fix-f 200 \
    --sg-fix-f 500 \
    --sg-fix-f 1000 

exit

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 1000 \
    --burst-family BTLWNB \
    --output wnb_test_2.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type fixed \
    --jitter 1.5 \
    --event-rate 1e5 \
    --wnb-max-dist 1   \
    --wnb-fix-egw 0.1  \
    --wnb-fix-egw 0.3  \
    --wnb-fix-egw 0.5  \
    --wnb-fix-bandwidth 10 \
    --wnb-fix-bandwidth 100 \
    --wnb-fix-duration 0.1 \
    --wnb-fix-duration 0.5 \
    --wnb-fix-duration 0.01 \
    --wnb-fix-frequency 200 \
    --wnb-fix-frequency 500 \
    --wnb-fix-frequency 1000 

exit

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 1000 \
    --burst-family BTLWNB \
    --output wnb_test.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type random \
    --event-rate 1e5 \
    --wnb-max-dist 1   \
    --wnb-min-egw 0.1 \
    --wnb-max-egw 0.5 \
    --wnb-min-bandwidth 10 \
    --wnb-max-bandwidth 100 \
    --wnb-min-duration 1e-2 \
    --wnb-max-duration 1e-1 \
    --wnb-min-frequency 10 \
    --wnb-max-frequency 1000 \
