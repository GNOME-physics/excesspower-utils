gps_start=9000
gps_end=11000
blocksize=131072
instrument=L1
channel=FAKE-STRAIN
ini_file=gstlal_excesspower.ini

all: injections excesspower addTriggers 

injections: 
	/home/sydc/excesspower-utils/bin/ligolw_binj \
	--gps-start-time 9900 \
	--gps-end-time 10000 \
	--burst-family SineGaussian \
	--output fixed_sg.xml.gz \
	--seed 1 \
	--time-slide-id 0 \
	--event-time-type fixed \
	--event-rate 1 \
	--sg-polarization-type linear \
	--sg-fix-hrss 1.104e2 \
	--sg-fix-q 9.8 \
	--sg-fix-f 100

excesspower:
	mkdir psd
	/home/sydc/gstlocal/bin/gstlal_excesspower --gps-start-time ${gps_start} --gps-end-time ${gps_end} --data-source white --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file} --injections fixed_sg.xml.gz

addTriggers:
	find L1/FAKE/STRAIN/ -name '*.xml.gz' | lalapps_path2cache -a > L1-FAKE_STRAIN_excesspower.cache
	ligolw_add -i L1-FAKE_STRAIN_excesspower.cache -v -o L1-FAKE_STRAIN_excesspower.xml.gz

clean:
	rm -f *.cache
	rm -rf L1
	rm -rf psd
	rm -f *.xml.gz
