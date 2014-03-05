START=1000000000
#STOP=1000086400
STOP=1000001000
DUR=$(shell python -c "print ${STOP}-${START}")

INJ_CHANNEL_NAME=FAKE-STRAIN
INJ_XML=mdc.xml.gz
INJECTION_FRAME_TYPE=aligo_inject_mdc
NOISE_FRAME_TYPE=aligo_noise_mdc

INJECTION_DEST=aligo_inject_mdc/
NOISE_DEST=aligo_noise_mdc/

LIGO_FRAME_DURATION=64 # s
LIGO_FRAME_DURATION_COMB=64 # s
LIGO_N_FRAMES=1

plots: H1_PSD_measured.png L1_PSD_measured.png V1_PSD_measured.png
	./plot_psds {H,L,V}1_PSD_measured.xml.gz

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
	./plot_psds_single H1 H1_PSD_measured.xml.gz H1_PSD_signal_measured.xml.gz
	mv psd_single.png H1_PSD_signal_measured.png

L1_PSD_signal_measured.xml.gz: L1_combined.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache L1_combined.cache --write-psd L1_PSD_signal_measured.xml.gz

L1_PSD_signal_measured.png: L1_PSD_signal_measured.xml.gz
	./plot_psds_single L1 L1_PSD_measured.xml.gz L1_PSD_signal_measured.xml.gz ../HLV-ILIGO_PSD.xml.gz
	mv psd_single.png L1_PSD_signal_measured.png

V1_PSD_signal_measured.xml.gz: V1_combined.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache V1_combined.cache --write-psd V1_PSD_signal_measured.xml.gz

V1_PSD_signal_measured.png: V1_PSD_signal_measured.xml.gz
	./plot_psds_single V1 V1_PSD_measured.xml.gz V1_PSD_signal_measured.xml.gz ../HLV-ILIGO_PSD.xml.gz
	mv psd_single.png V1_PSD_signal_measured.png

H1_PSD_measured.xml.gz: H1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel H1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache H1_aligo_noise.cache --write-psd H1_PSD_measured.xml.gz

H1_PSD_measured.png: H1_PSD_measured.xml.gz
	./plot_psds_single H1 H1_PSD_measured.xml.gz ../HLV-ILIGO_PSD.xml.gz
	mv psd_single.png H1_PSD_measured.png

L1_PSD_measured.xml.gz: L1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel L1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache L1_aligo_noise.cache --write-psd L1_PSD_measured.xml.gz

L1_PSD_measured.png: L1_PSD_measured.xml.gz
	./plot_psds_single L1 L1_PSD_measured.xml.gz ../HLV-ILIGO_PSD.xml.gz
	mv psd_single.png L1_PSD_measured.png

V1_PSD_measured.xml.gz: V1_aligo_noise.cache
	gstlal_reference_psd --gps-start-time ${START} --gps-end-time ${STOP} --channel V1=${INJ_CHANNEL_NAME} --verbose --data-source frames --frame-cache V1_aligo_noise.cache --write-psd V1_PSD_measured.xml.gz

V1_PSD_measured.png: V1_PSD_measured.xml.gz
	./plot_psds_single V1 V1_PSD_measured.xml.gz ../HLV-ILIGO_PSD.xml.gz
	mv psd_single.png V1_PSD_measured.png

clean:
	rm *.cache
	rm -rf aligo_noise_mdc/
	rm -rf aligo_inject_mdc/
	rm -rf aligo_inject_combined/
	rm -rf *_measured_*.xml.gz
	rm -rf *.png
