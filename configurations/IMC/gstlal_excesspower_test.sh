#!/bin/bash
channel_name="IMC-F_OUT_DQ"
sample_rate=4096
init_file=something.ini
frame_cache=something.cache

gstlal_excesspower --data-source frames --channel-name L1=${channel_name} --sample-rate ${sample_rate} --initialization-file ${init_file} --verbose --clustering --frame-cache ${frame_cache} --verbose
