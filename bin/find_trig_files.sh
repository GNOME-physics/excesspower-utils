#!/bin/bash

find $1 -name "*.xml.gz" | lalapps_path2cache > $2
