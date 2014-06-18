gps_start=8000
gps_end=12000
blocksize=131072
instrument=L1
channel=FAKE-STRAIN
ini_file=gstlal_excesspower.ini

/home/sydc/gstlocal/bin/gstlal_excesspower --gps-start-time ${gps_start} --gps-end-time ${gps_end} --data-source white --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file} --injections fixed_sg.xml.gz

