EP_PATH=/home/pankow/excesspower/excesspower-utils/utilities/

START=$(shell lalapps_tconvert Oct 19 6:17:00)
STOP=$(shell lalapps_tconvert Oct 19 7:17:00)

CHANNELS="L1:LSC-MICH_IN1_DQ\|L1:LSC-MICH_OUT_DQ\|L1:LSC-PRCL_IN1_DQ\|L1:LSC-PRCL_OUT_DQ\|L1:LSC-SRCL_IN1_DQ\|L1:LSC-SRCL_OUT_DQ\|L1:OMC-LSC_SERVO_INMON\|L1:OMC-LSC_SERVO_OUT_DQ\|L1:LSC-OMC_DC_OUT_DQ\|L1:LSC-POPAIR_B_RF18_I_ERR_DQ"

all: PRMI.dag
	mkdir spectra
	mkdir triggers

L1_R_frames.cache:
	# The sed command is to ensure L1 is in the type
	ligo_data_find -o L -u file -t R -s ${START} -e ${STOP} -l | sed s/\ R/\ L1_R/g > L1_R_frames.cache

prmi_channels.ini: L1_R_frames.cache
	FrChannels $(shell ligo_data_find -o L -u file -t R -s ${START} -e ${STOP} | head -1) | grep ${CHANNELS} | ${EP_PATH}make_ini_file.py > prmi_channels.ini

PRMI.dag: L1_R_frames.cache prmi_channels.ini
	# FIXME: Segments
	${EP_PATH}make_ep_channel_dag --begin-gps-time ${START} --end-gps-time ${STOP} --submit-file ./gstlal_excesspower_2cpu.sub --output PRMI.dag --initialization-file ./prmi_channels.ini
