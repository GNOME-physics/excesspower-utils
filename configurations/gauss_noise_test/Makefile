gps_start=8000
gps_end=12000
blocksize=131072
instrument=L1
channel=FAKE-STRAIN
ini_file=gstlal_excesspower.ini
hrss=e+10

all: injections excesspower addTriggers plot

zero_lag.xml.gz:
	ligolw_tisi -i H1=0:0:1 -i L1=0:0:1 -i V1=0:0:1 > zero_lag.xml
	gzip zero_lag.xml

fixed_sg.xml.gz: zero_lag.xml.gz
	../../bin/ligolw_binj \
	--gps-start-time 9900 \
	--gps-end-time 10000 \
	--burst-family SineGaussian \
	--output fixed_sg.xml.gz \
	--seed 1 \
	--time-slide-id 0 \
	--event-time-type fixed \
	--event-rate 1 \
	--sg-polarization-type linear \
	--sg-fix-hrss 1.104${hrss} \
	--sg-fix-q 9.8 \
	--sg-fix-f 100
	ligolw_add -o $@ $@ $<

excesspower: fixed_sg.xml.gz
	mkdir psd
	gstlal_excesspower --gps-start-time ${gps_start} --gps-end-time ${gps_end} --data-source white --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file} --injections $<

addTriggers:
	find L1/FAKE/STRAIN/ -name '*.xml.gz' | lalapps_path2cache -a > L1-FAKE_STRAIN_excesspower.cache
	ligolw_add -i L1-FAKE_STRAIN_excesspower.cache -v -o L1-FAKE_STRAIN_excesspower.xml.gz

plot:
	gstlal_excesspower_trigvis L1-FAKE_STRAIN_excesspower.xml.gz -j fixed_sg.xml.gz -O 0.3 -o ~/public_html/fixedSnr/fixed_sg_${hrss} -s 8000 -e 12000

clean:
	rm -f *.cache
	rm -rf L1
	rm -rf psd
	rm -f *.xml.gz
