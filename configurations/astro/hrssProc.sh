#/bin/bash
rm *.cache *.sqlite

psd_file=L1_PSD_measured.xml.gz
unclustered_triggers=unclustered_results/L1-FAKE_STRAIN_Triggers.xml.gz

echo "using python to write unclustered triggers to file..."
python modEpAmplitude.py --det-psd-file ${psd_file} --triggers ${unclustered_triggers}

for i in unc_*; do

file_name=${i#*_}
cache_name=${file_name%%.*}
echo "now running on file ${file_name} to create series ${cache_name}.\n"

echo "generating cache from triggers..."
find . -name 'unc_'${file_name} | lalapps_path2cache -a > ${cache_name}.cache

# clustering
echo "clustering...\n"
echo "     ligolw_bucluster --cluster-algorithm excesspower -i ${cache_name}.cache -p gstlal_excesspower -v\n"
ligolw_bucluster --cluster-algorithm excesspower -i ${cache_name}.cache -p gstlal_excesspower -v
echo "clustering done." 

# add it all into one xml file
echo "conglomerating...\n"
echo "     ligolw_add -i ${cache_name}.cache zero_lag.xml.gz L-FAKE_SEARCH.xml.gz -o ${cache_name}.xml.gz -v\n"
ligolw_add -i ${cache_name}.cache ~/excesspower-utils/configurations/astro/zero_lag.xml.gz L-FAKE_SEARCH.xml.gz -o ${cache_name}.xml.gz -v

# run binjfind
echo "running ligolw_binjfind...\n"
echo "     ligolw_binjfind ${cache_name}.xml.gz -c excesspower -v \n"
ligolw_binjfind ${cache_name}.xml.gz -c excesspower -v 
ls ${cache_name}.xml.gz | lalapps_path2cache -a > ${cache_name}.cache

# and now make into a sqlite database... 
echo "creating sqlite database...\n"
echo "     ligolw_sqlite -i ${cache_name}.cache -t /usr1/sydc -d ${cache_name}.sqlite -v\n" 
ligolw_sqlite -i ${cache_name}.cache -t /usr1/sydc -d ${cache_name}.sqlite -v

# now run lalapps_power_plot_binj
echo "running power_plot_binj...\n"
echo "     ./sc_lal_ppb --amplitude-func hrssdet -l gstlal_excesspower -t /usr1/sydc/ -v ${cache_name}.sqlite --coinc-plot none\n"
./sc_lal_ppb --amplitude-func hrssdet -l gstlal_excesspower -t /usr1/sydc/ -v ${cache_name}.sqlite --coinc-plot none

echo "giving plots more suitable names..."
for i in plotbinj*; do mv "$i" ${cache_name}_"${i}"; done

echo "cleaning up directory..."
mkdir ${cache_name}'_files'
zip ${cache_name} ${cache_name}*
mv 'ms_snr.txt' ${cache_name}_'ms_snr.txt'
mv ${cache_name}_'plotbinj'* ${cache_name}'_files';

done
