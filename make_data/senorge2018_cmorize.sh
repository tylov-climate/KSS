#/bin/bash
input=/nird/projects/NS9001K/tyge/seNorge2018
outdir=../../seNorge2018_cmor
#outdir=/nird/projects/NS9076K/data/cordex-norway/seNorge2018_cmor
mkdir -p $outdir

for i in $(seq $1 $2); do
    if [ ! -f seNorge2018_${i}_remap.nc ]; do
        cdo remapbil,griddes.txt $input/seNorge2018_$i.nc seNorge2018_${i}_remap.nc
    fi

    cdo selvar,rr seNorge2018_${i}_remap.nc pr1_$i.nc
    ncrename -O -v rr,pr pr1_$i.nc pr2_$i.nc
    ncap2 -O -s "pr=pr/86400" pr2_$i.nc pr1_$i.nc
    ncatted -O -a units,pr,o,c,"kg m-2 s-1" -a standard_name,pr,o,c,"precipitation_flux" -a long_name,pr,o,c,"Precipitation" pr1_$i.nc  $outdir/pr_seNorge2018_${i}_remap.nc
    rm pr1_$i.nc pr2_$i.nc

    cdo selvar,tg seNorge2018_${i}_remap.nc tas1_$i.nc
    ncrename -O -v tg,tas tas1_$i.nc tas2_$i.nc
    ncap2 -O -s "tas=tas+273.15" tas2_$i.nc tas1_$i.nc
    ncatted -O -a units,tas,o,c,"K" -a long_name,tas,o,c,"Near-Surface Air Temperature" tas1_$i.nc  $outdir/tas_seNorge2018_${i}_remap.nc
    rm tas1_$i.nc tas2_$i.nc
    # comment this to keep non-processed remapped files:
    rm seNorge2018_${i}_remap.nc
done
