#/bin/bash

find L1/FAKE/STRAIN/ -name '*.xml.gz' | lalapps_path2cache -a > L1-FAKE_STRAIN_excesspower.cache
ligolw_add -i L1-FAKE_STRAIN_excesspower.cache -v -o L1-FAKE_STRAIN_excesspower.xml.gz
