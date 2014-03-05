START=1000000000
#STOP=1000086400
STOP=1000001000
DUR=$(shell python -c "print ${STOP}-${START}")

INJ_CHANNEL_NAME=FAKE-STRAIN
INJ_XML=test_sg150q9.xml.gz
INJECTION_FRAME_TYPE=aligo_inject_mdc
NOISE_FRAME_TYPE=aligo_noise_mdc

INJECTION_DEST=aligo_inject_mdc/
NOISE_DEST=aligo_noise_mdc/

LIGO_FRAME_DURATION=64 # s
LIGO_FRAME_DURATION_COMB=64 # s
LIGO_N_FRAMES=1

all: aligo_inject_combined.cache plots

#
# Injection tables
#
zero_lag.xml.gz:
	ligolw_tisi -i H1=0:0:1 -i L1=0:0:1 -i V1=0:0:1 > zero_lag.xml
	gzip zero_lag.xml

test_sg150q9.xml.gz: zero_lag.xml.gz
	../../bin/ligolw_binj  \
    	--gps-start-time ${START}  \
    	--gps-end-time ${STOP}  \
    	--seed 0 \
    	--event-time-type fixed  \
    	--event-rate 3e6  \
    	--burst-family SineGaussian  \
    	--sg-fix-q 9  \
    	--sg-fix-f 150  \
    	--sg-fix-hrss 1e-19  \
    	--sg-polarization-type circular  \
    	--output $@

	ligolw_add -v -o $@ $@ $<

astroInjections.xml.gz: zero_lag.xml.gz
	../../bin/ligolw_binj \
    	--gps-start-time 0 \
    	--gps-end-time 6000 \
    	--output astroInjections.xml.gz \
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

	ligolw_add -v -o $@ $@ $<

#
# Diagnostic plots
#
plots: H1_PSD_measured.png L1_PSD_measured.png V1_PSD_measured.png
	./plot_psds {H,L,V}1_PSD_measured.xml.gz

#
#  Data generation
#
aligo_inject.cache: H1_aligo_inject.cache L1_aligo_inject.cache V1_aligo_inject.cache
	cat {H,L,V}1_aligo_inject.cache > aligo_inject.cache

H1_aligo_inject.cache: ${INJ_XML}
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --injections ${INJ_XML} --channel H1=${INJ_CHANNEL_NAME} --verbose --data-source silence --output-channel ${INJ_CHANNEL_NAME} --frame-type H1_${INJECTION_FRAME_TYPE} --output-path ${INJECTION_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${INJECTION_DEST}/ -name "H-*.gwf" | lalapps_path2cache > H1_aligo_inject.cache

L1_aligo_inject.cache: ${INJ_XML}
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --injections ${INJ_XML} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source silence --output-channel ${INJ_CHANNEL_NAME} --frame-type L1_${INJECTION_FRAME_TYPE} --output-path ${INJECTION_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${INJECTION_DEST}/ -name "L-*.gwf" | lalapps_path2cache > L1_aligo_inject.cache

V1_aligo_inject.cache: ${INJ_XML}
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --injections ${INJ_XML} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source silence --output-channel ${INJ_CHANNEL_NAME} --frame-type V1_${INJECTION_FRAME_TYPE} --output-path ${INJECTION_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${INJECTION_DEST}/ -name "V-*.gwf" | lalapps_path2cache > V1_aligo_inject.cache

H1_aligo_noise.cache:
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --channel H1=${INJ_CHANNEL_NAME} --verbose --data-source LIGO --output-channel ${INJ_CHANNEL_NAME} --frame-type H1_${NOISE_FRAME_TYPE} --output-path ${NOISE_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${NOISE_DEST}/ -name "H-*.gwf" | lalapps_path2cache > H1_aligo_noise.cache

L1_aligo_noise.cache:
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source LIGO --output-channel ${INJ_CHANNEL_NAME} --frame-type L1_${NOISE_FRAME_TYPE} --output-path ${NOISE_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${NOISE_DEST}/ -name "L-*.gwf" | lalapps_path2cache > L1_aligo_noise.cache

V1_aligo_noise.cache:
	gstlal_fake_frames --gps-start-time ${START} --gps-end-time ${STOP} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source LIGO --output-channel ${INJ_CHANNEL_NAME} --frame-type V1_${NOISE_FRAME_TYPE} --output-path ${NOISE_DEST} --frame-duration ${LIGO_FRAME_DURATION} --frames-per-file ${LIGO_N_FRAMES}
	find ${NOISE_DEST}/ -name "V-*.gwf" | lalapps_path2cache > V1_aligo_noise.cache

H1_combined.cache: H1_aligo_noise.cache H1_aligo_inject.cache
	./add_frames H1_aligo_noise.cache H1_aligo_inject.cache H1
	mkdir -p aligo_inject_combined/
	mv H-*.gwf aligo_inject_combined
	find aligo_inject_combined/ -name "H-*.gwf" | lalapps_path2cache > H1_combined.cache

L1_combined.cache: L1_aligo_noise.cache L1_aligo_inject.cache
	./add_frames L1_aligo_noise.cache L1_aligo_inject.cache L1
	mkdir -p aligo_inject_combined/
	mv L-*.gwf aligo_inject_combined
	find aligo_inject_combined/ -name "L-*.gwf" | lalapps_path2cache > L1_combined.cache

V1_combined.cache: V1_aligo_noise.cache V1_aligo_inject.cache
	./add_frames V1_aligo_noise.cache V1_aligo_inject.cache V1
	mkdir -p aligo_inject_combined/
	mv V-*.gwf aligo_inject_combined
	find aligo_inject_combined/ -name "V-*.gwf" | lalapps_path2cache > V1_combined.cache

aligo_inject_combined.cache: H1_combined.cache L1_combined.cache V1_combined.cache
	cat {H,L,V}1_combined.cache > aligo_inject_combined.cache

aligo_noise.cache: H1_combined.cache L1_combined.cache V1_combined.cache
	cat {H,L,V}1_aligo_noise.cache > aligo_noise.cache

H1_PSD_signal_measured.xml.gz: H1_combined.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel H1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache H1_combined.cache --write-psd H1_PSD_signal_measured.xml.gz

H1_PSD_signal_measured.png: H1_PSD_signal_measured.xml.gz
	./plot_psds_single H1 $@ H1_PSD_measured.xml.gz H1_PSD_signal_measured.xml.gz

L1_PSD_signal_measured.xml.gz: L1_combined.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache L1_combined.cache --write-psd L1_PSD_signal_measured.xml.gz

L1_PSD_signal_measured.png: L1_PSD_signal_measured.xml.gz
	./plot_psds_single L1 $@ L1_PSD_measured.xml.gz L1_PSD_signal_measured.xml.gz

V1_PSD_signal_measured.xml.gz: V1_combined.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache V1_combined.cache --write-psd V1_PSD_signal_measured.xml.gz

V1_PSD_signal_measured.png: V1_PSD_signal_measured.xml.gz
	./plot_psds_single V1 $@ V1_PSD_measured.xml.gz V1_PSD_signal_measured.xml.gz

H1_PSD_measured.xml.gz: H1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel H1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache H1_aligo_noise.cache --write-psd H1_PSD_measured.xml.gz

H1_PSD_measured.png: H1_PSD_measured.xml.gz
	./plot_psds_single H1 $@ $<

L1_PSD_measured.xml.gz: L1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache L1_aligo_noise.cache --write-psd L1_PSD_measured.xml.gz

L1_PSD_measured.png: L1_PSD_measured.xml.gz
	./plot_psds_single L1 $@ $<

V1_PSD_measured.xml.gz: V1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache V1_aligo_noise.cache --write-psd V1_PSD_measured.xml.gz

V1_PSD_measured.png: V1_PSD_measured.xml.gz
	./plot_psds_single V1 $@ $<

clean:
	rm *.cache
	rm -rf aligo_noise_mdc/
	rm -rf aligo_inject_mdc/
	rm -rf aligo_inject_combined/
	rm -rf *_measured_*.xml.gz
	rm -rf *.png
