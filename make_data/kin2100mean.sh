echo ""
echo === ENSEMBLE $2 OF MONTHLY $3 TEMPERATURE NORWAY 1971-2100 ===
echo ""
cdo=/opt/cdo

for f in $1/tas_*.nc; do

    echo $f
    echo ""
    echo MONTHLY:
    $cdo fldmean $f tmp.nc > /dev/null
    ncdump -v tas tmp.nc | sed -e '1,/data:/d' -e '$d'
    $cdo timmean $f tmp.nc > /dev/null
    $cdo fldmean tmp.nc tmp2.nc > /dev/null
    echo ""
    echo TOTAL:
    ncdump -v tas tmp2.nc | sed -e '1,/data:/d' -e '$d'
    echo ""

done

echo ""
echo === ENSEMBLE $2 OF MONTHLY $3 PRECIPTIATION NORWAY 1971-2100 ===
echo ""

for f in $1/pr_*.nc; do

    echo $f
    echo ""
    echo MONTHLY:
    $cdo fldmean $f tmp.nc > /dev/null
    ncdump -v pr tmp.nc | sed -e '1,/data:/d' -e '$d'
    $cdo timmean $f tmp.nc > /dev/null
    $cdo fldmean tmp.nc tmp2.nc > /dev/null
    echo ""
    echo TOTAL:
    ncdump -v pr tmp2.nc | sed -e '1,/data:/d' -e '$d'
    echo ""

done

rm -f tmp.nc tmp2.nc
