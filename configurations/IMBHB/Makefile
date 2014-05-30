START=966383946
#END=971621451
END=966393946
DUR=$(shell python -c "print ${END} - ${START}")

print_dur:
	@echo ${DUR}

H1_aLIGO_IMBHB_unclustered.cache: H1
	find $< -name "*.xml.gz" | lalapps_path2cache > $@
L1_aLIGO_IMBHB_unclustered.cache: L1
	find $< -name "*.xml.gz" | lalapps_path2cache > $@

H1_triggers_clustered: H1
	cp -r $< $@
L1_triggers_clustered: L1
	cp -r $< $@

H1_aLIGO_IMBHB_clustered.cache: H1_triggers_clustered
	find $< -name "*.xml.gz" | lalapps_path2cache > .h1tmp
	ligolw_bucluster -v -c excesspower -p gstlal_excesspower -i .h1tmp 
	mv .h1tmp $@
L1_aLIGO_IMBHB_clustered.cache: L1_triggers_clustered
	find $< -name "*.xml.gz" | lalapps_path2cache > .l1tmp
	ligolw_bucluster -v -c excesspower -p gstlal_excesspower -i .l1tmp 
	mv .l1tmp $@

HL_aLIGO_IMBHB_clustered.cache: H1_aLIGO_IMBHB_clustered.cache L1_aLIGO_IMBHB_clustered.cache
	cat H1_aLIGO_IMBHB_clustered.cache L1_aLIGO_IMBHB_clustered.cache > $@

tisi.xml.gz:
	ligolw_tisi -v -i H1=0:10:1 -i L1=0:0:1  > tisi.xml
	gzip tisi.xml

tisi_zero.xml.gz:
	ligolw_tisi -v -i H1=0:0:1 -i L1=0:0:1  > tisi_zero.xml
	gzip tisi_zero.xml
	
hl_combined_sim: HL_aLIGO_IMBHB_clustered.cache tisi_zero.xml.gz IMBHB-MDC-50-50.xml.gz
	ligolw_add -i $< -o HL-IMBHB_MDC-${START}-${DUR}.xml.gz IMBHB-MDC-50-50.xml.gz tisi_zero.xml.gz

hl_combined_bkg: HL_aLIGO_IMBHB_clustered.cache tisi.xml.gz
	ligolw_add -i $< -o HL-IMBHB_MDC_BKG-${START}-${DUR}.xml.gz tisi.xml.gz

burca_bkg: HL-IMBHB_MDC_BKG-${START}-${DUR}.xml.gz 
	ligolw_burca -v -a excesspower -t "H1,L1=0" $<

burca_sim: HL-IMBHB_MDC-${START}-${DUR}.xml.gz 
	ligolw_burca -v -a excesspower -t "H1,L1=0" $<

burca: burca_bkg burca_sim

binjfind: HL-IMBHB_MDC-${START}-${DUR}.xml.gz 
	ligolw_binjfind -c excesspower -v $<

databases: databases_sim databases_bkg

databases_sim: HL-IMBHB_MDC-${START}-${DUR}.xml.gz 
	ligolw_sqlite -v -t /dev/shm/ -d HL-IMBHB_MDC-${START}-${DUR}.sqlite $<

databases_bkg: HL-IMBHB_MDC_BKG-${START}-${DUR}.xml.gz 
	ligolw_sqlite -v -t /dev/shm/ -d HL-IMBHB_MDC_BKG-${START}-${DUR}.sqlite $<

farburst: HL-IMBHB_MDC-${START}-${DUR}.sqlite HL-IMBHB_MDC_BKG-${START}-${DUR}.sqlite 
	lalapps_farburst -p gstlal_excesspower --rank-by snr -t /dev/shm/ -v HL-IMBHB_MDC*-966383946-10000.sqlite

postprocess: hl_combined_bkg hl_combined_sim burca binjfind databases farburst web

web:
	make -C web/

.PHONY: burca burca_sim burca_bkg databases databases_sim databases_bkg farburst binjfind hl_combined_bkg hl_combined_sim

h1_run_ep: aLIGO_IMBHB_MDC_data.cache aLIGO_IMBHB_MDC.ini IMBHB-MDC-150-150.xml.gz
	gstlal_excesspower  \
		--verbose  \
		--initialization-file aLIGO_IMBHB_MDC.ini  \
		--gps-start-time ${START}  \
		--gps-end-time ${END}  \
		--channel-name H1=GAUSSIAN  \
		--data-source frames  \
		--frame-cache aLIGO_IMBHB_MDC_data.cache  \
		--injections IMBHB-MDC-150-150.xml.gz

l1_run_ep: aLIGO_IMBHB_MDC_data.cache aLIGO_IMBHB_MDC.ini IMBHB-MDC-150-150.xml.gz
	gstlal_excesspower  \
		--verbose  \
		--initialization-file aLIGO_IMBHB_MDC.ini  \
		--gps-start-time ${START}  \
		--gps-end-time ${END}  \
		--channel-name L1=GAUSSIAN  \
		--data-source frames  \
		--frame-cache aLIGO_IMBHB_MDC_data.cache  \
		--injections IMBHB-MDC-150-150.xml.gz

h1_available_data:
	ligo_data_find -o H --show-times -t H1_T1200307_V4_EARLY_GAUSSIAN
l1_available_data:
	ligo_data_find -o L --show-times -t L1_T1200307_V4_EARLY_GAUSSIAN

aLIGO_IMBHB_MDC_data.cache:
	ligo_data_find -o H -s ${START} -e ${END} -t H1_T1200307_V4_EARLY_GAUSSIAN -u file -l > .h1tmp.cache
	ligo_data_find -o L -s ${START} -e ${END} -t L1_T1200307_V4_EARLY_GAUSSIAN -u file -l > .l1tmp.cache
	cat .h1tmp.cache .l1tmp.cache > $@
	rm .{h,l}1tmp.cache
