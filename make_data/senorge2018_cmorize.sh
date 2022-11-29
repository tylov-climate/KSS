#/bin/bash
input=/nird/projects/NS9001K/tyge/seNorge2018
out=../..seNorge2018_cmor
mkdir -p $out

for i in $(seq $1 $2); do
    cdo remapbil,griddes.txt $input/seNorge2018_$i.nc seNorge2018_${i}_remap.nc

    cdo selvar,rr seNorge2018_${i}_remap.nc pr1_$i.nc
    ncrename -O -v rr,pr pr1_$i.nc pr2_$i.nc
    ncap2 -O -s "pr=pr/86400" pr2_$i.nc pr1_$i.nc
    ncatted -O -a units,pr,o,c,"kg m-2 s-1" -a standard_name,pr,o,c,"precipitation_flux" -a long_name,pr,o,c,"Precipitation" pr1_$i.nc  $out/pr_seNorge2018_${i}_remap.nc
    #  ../stats_v3/yseasmean/pr_yseasmean_1951-2000_histo/pr_EUR-11_seNorge_seNorge2018_historical_r1i1p1_None_v1_yseasmean_v20190101_1951-2000.nc
    rm pr1_$i.nc pr2_$i.nc

    cdo selvar,tg seNorge2018_${i}_remap.nc tas1_$i.nc
    ncrename -O -v tg,tas tas1_$i.nc tas2_$i.nc
    ncap2 -O -s "tas=tas+273.15" tas2_$i.nc tas1_$i.nc
    ncatted -O -a units,tas,o,c,"K" -a long_name,tas,o,c,"Near-Surface Air Temperature" tas1_$i.nc  $out/tas_seNorge2018_${i}_remap.nc
    # ../stats_v3/yseasmean/tas_yseasmean_1951-2000_histo/tas_EUR-11_seNorge_seNorge2018_historical_r1i1p1_None_v1_yseasmean_v20190101_1951-2000.nc
    rm tas1_$i.nc tas2_$i.nc
    rm seNorge2018_${i}_remap.nc
done
