#!/bin/bash
channel_name="IMC-F_OUT_DQ"
sample_rate=4096
init_file=config.txt
frame_cache=something.cache
start=1076669952
end=1076670952

gstlal_excesspower \
    --data-source frames \
    --channel-name L1=${channel_name} \
    --sample-rate ${sample_rate} \
    --gps-start-time ${start} \
    --gps-end-time ${end} \
    --frame-cache ${frame_cache} \
    --write-psd L1-${channel_name}_REF_PSD.xml.gz \
    --verbose
    # possibly also useful
    #--psd-fft-length 8
