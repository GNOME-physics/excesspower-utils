#!/bin/bash

./ligolw_binj \
    --gps-start-time 0 \
    --gps-end-time 6000 \
    --output astroInjections.xml \
    --seed 1 \
    --time-slide-id 0 \
    --event-time-type fixed  \
    --event-rate 1.05e6  \
    --burst-family BTLWNB \
    --wnb-min-egw 1e-7 \
    --wnb-max-egw 1e-2 \
    --wnb-min-bandwidth 50 \
    --wnb-max-bandwidth 1500 \
    --wnb-min-duration 0.001 \
    --wnb-max-duration 0.02 \
    --wnb-min-frequency 65 \
    --wnb-max-frequency 4000  \
    --burst-family SineGaussian \
    --sg-polarization-type linear \
    --sg-min-q 3 \
    --sg-max-q 9 \
    --sg-min-f 40 \
    --sg-max-f 4000 \
    --sg-min-hrss 1e-24 \
    --sg-max-hrss 1e-20

exit
