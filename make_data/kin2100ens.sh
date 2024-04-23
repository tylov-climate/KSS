# $1 = path to statisics folder
# $2 = mean, min, or max over variable

echo ""
echo === Ensemble mean of seasonal $2 temperature, Norway 1971-2100 ===
echo ""
cdo='cdo -w'

for f in $1/ensmean_yseas$2/tas_*.nc; do

    echo ""
    echo $(basename $f):
    echo ""
    echo -n SEASONAL:
    $cdo fldmean $f tmp.nc > /dev/null
    ncdump -v tas tmp.nc | sed -e '1,/^data:/d' -e '$d'
    $cdo timmean $f tmp.nc > /dev/null
    $cdo fldmean tmp.nc tmp2.nc > /dev/null
    echo ""
    echo -n TOTAL:
    ncdump -v tas tmp2.nc | sed -e '1,/^data:/d' -e '$d'
    echo ""

done

echo ""
echo === Ensemble mean of seasonal $2 precipitation, Norway 1971-2100 ===
echo ""

for f in $1/ensmean_yseas$2/pr_*.nc; do

    echo ""
    echo $(basename $f):
    echo ""
    echo -n SEASONAL:
    $cdo fldmean $f tmp.nc > /dev/null
    ncdump -v pr tmp.nc | sed -e '1,/^data:/d' -e '$d'
    $cdo timmean $f tmp.nc > /dev/null
    $cdo fldmean tmp.nc tmp2.nc > /dev/null
    echo ""
    echo -n TOTAL:
    ncdump -v pr tmp2.nc | sed -e '1,/^data:/d' -e '$d'
    echo ""

done

rm -f tmp.nc tmp2.nc
