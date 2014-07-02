gps_start=8000
gps_end=12000
blocksize=131072
instrument=L1
channel=FAKE-STRAIN
ini_file=gstlal_excesspower.ini
hrss=e+1

all: injections excesspower addTriggers plot

L1-FAKE_STRAIN_PSD_measured.xml.gz: L1_gauss_frames.cache
	gstlal_reference_psd \
		--gps-start-time 9500  \
		--gps-end-time 10100  \
		--data-source frames  \
		--frame-cache $<  \
		--sample-rate 4096  \
		--verbose  \
		--channel-name ${instrument}=${channel} \
		--write-psd $@

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

L1_gauss_frames.cache: fixed_sg.xml.gz
	gstlal_fake_frames  \
		--gps-start-time ${gps_start}  \
		--gps-end-time ${gps_end}  \
		--data-source white  \
		--sample-rate 4096  \
		--verbose  \
		--channel-name ${instrument}=${channel}  \
		--frame-type L1_FIXED_GAUSS  \
		--frame-duration 1024  \
		--frames-per-file 1  \
		--output-path gauss_noise \
		--injections $<
	find gauss_noise -name "*.gwf" | lalapps_path2cache > $@

excesspower: fixed_sg.xml.gz
	mkdir -p psd
	gstlal_excesspower --gps-start-time ${gps_start} --gps-end-time ${gps_end} --data-source white --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file} --injections $<

excesspower_frames: L1_gauss_frames.cache
	mkdir -p psd
	gstlal_excesspower --gps-start-time 9000 --gps-end-time 10010 --data-source frames --frame-cache $< --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file}

excesspower_scan: L1_gauss_frames.cache
	mkdir -p psd
	./gstlal_excesspower --gps-start-time 9000 --gps-end-time 10010 --data-source frames --frame-cache $< --sample-rate 4096 -v --channel-name ${instrument}=${channel} -f ${ini_file} --scan-segment-start 9999.95 --scan-segment-end 10000.05

addTriggers:
	find L1/FAKE/STRAIN/ -name '*.xml.gz' | lalapps_path2cache -a > L1-FAKE_STRAIN_excesspower.cache
	ligolw_add -i L1-FAKE_STRAIN_excesspower.cache -v -o L1-FAKE_STRAIN_excesspower.xml.gz

plot:
	#gstlal_excesspower_trigvis L1-FAKE_STRAIN_excesspower.xml.gz -j fixed_sg.xml.gz -O 0.3 -o fixed_sg_${hrss} -s 9999 -e 10001
	gstlal_excesspower_trigvis /home/pankow/excesspower/excesspower-utils/configurations/gauss_noise_test/L1/FAKE/STRAIN/9800/L1-FAKE_STRAIN_excesspower-9800-600.xml.gz -j fixed_sg.xml.gz -O 0.3 -o fixed_sg_${hrss} -s 9999 -e 10001 -F 200

clean:
	rm -f *.cache
	rm -rf L1
	rm -rf psd
	rm -f *.xml.gz
