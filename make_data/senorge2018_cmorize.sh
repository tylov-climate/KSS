#/bin/bash
cdo selvar,rr seNorge2018_1951-2000.nc tmp1.nc
ncrename -O -v rr,pr tmp1.nc tmp2.nc
ncap2 -O -s "pr=pr/86400" tmp2.nc tmp1.nc
ncatted -O -a units,pr,o,c,"kg m-2 s-1" -a standard_name,pr,o,c,"precipitation_flux" -a long_name,pr,o,c,"Precipitation" tmp1.nc ../stats_v3/yseasmean/pr_yseasmean_1951-2000_histo/pr_EUR-11_seNorge_seNorge2018_historical_r1i1p1_None_v1_yseasmean_v20190101_1951-2000.nc

cdo selvar,tg seNorge2018_1951-2000.nc tmp1.nc
ncrename -O -v tg,tas tmp1.nc tmp2.nc
ncap2 -O -s "tas=tas+273.15" tmp2.nc tmp1.nc
ncatted -O -a units,tas,o,c,"K" -a long_name,tas,o,c,"Near-Surface Air Temperature" tmp1.nc ../stats_v3/yseasmean/tas_yseasmean_1951-2000_histo/tas_EUR-11_seNorge_seNorge2018_historical_r1i1p1_None_v1_yseasmean_v20190101_1951-2000.nc

rm tmp1.nc tmp2.nc