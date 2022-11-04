op=mean
#op=max
#op=ens-mean
#op=ens-max
if [ ! -z $1 ]; then op=$1; fi

echo "generate log files for $op"
for m in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
    echo start $m
    python make_stats.py --dry -s $op -m $m > logs/$m.log
done

echo "run $op stats the background"
for m in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
    python make_stats.py -s $op -m $m >& /dev/null &
done

exit

python make_stats.py -s mean CLMcom
python make_stats.py -s mean CLMcom-BTU
python make_stats.py -s mean CLMcom-ETH
python make_stats.py -s mean CNRM
python make_stats.py -s mean DMI
python make_stats.py -s mean GERICS
python make_stats.py -s mean ICTP
python make_stats.py -s mean IPSL
python make_stats.py -s mean KNMI
python make_stats.py -s mean MOHC
python make_stats.py -s mean MPI-CSC
python make_stats.py -s mean RMIB-UGent
python make_stats.py -s mean SMHI
python make_stats.py -s mean UHOH
