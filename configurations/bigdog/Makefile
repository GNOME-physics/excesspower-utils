ETIME=968654558
START=$(shell python -c "print ${ETIME} - 2*3600")
END=$(shell python -c "print ${ETIME} + 2*3600")
DUR=$(shell python -c "print ${END} - ${START}")
H1_FRTYPE=H1_LDAS_C02_L2
L1_FRTYPE=L1_LDAS_C02_L2
V1_FRTYPE=HrecV2

print_dur:
	@echo ${DUR}

h1_available_data:
	ligo_data_find -o H --show-times -t ${H1_FRTYPE}
l1_available_data:
	ligo_data_find -o L --show-times -t ${L1_FRTYPE}
v1_available_data:
	ligo_data_find -o V --show-times -t ${L1_FRTYPE}

big_dog.cache:
	ligo_data_find --gaps -o H -s ${START} -e ${END} -t ${H1_FRTYPE} -u file -l > .h1tmp.cache
	ligo_data_find --gaps -o L -s ${START} -e ${END} -t ${L1_FRTYPE} -u file -l > .l1tmp.cache
	ligo_data_find --gaps -o V -s ${START} -e ${END} -t ${V1_FRTYPE} -u file -l > .v1tmp.cache
	cat .h1tmp.cache .l1tmp.cache .v1tmp.cache > $@
	rm .h1tmp.cache .l1tmp.cache .v1tmp.cache

excesspower.dag: big_dog.cache
	PYTHONPATH=/home/pankow/excesspower/excesspower-utils/python:${PYTHONPATH} \
	/home/pankow/excesspower/excesspower-utils/bin/ep_trigger_pipe \
		--gps-start-time ${START} \
		--gps-end-time ${END} \
		--subsystem-ini-file s6_strain.ini \
		--frame-cache $< \
		--trigger-directory /home/pankow/excesspower/excesspower-utils/configurations/bigdog \
		--write-script

