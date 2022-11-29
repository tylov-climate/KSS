iv=ymon
#op=mean
op=max
#op=mean --ensemble
#op=max --ensemble
if [ ! -z $1 ]; then op=$1; fi

echo "generate log files for $op"
for m in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
    echo start $m
    python make_stats.py --dry -s $op --interval $iv -m $m > logs/$m.log
done

echo "run $op stats the background"
for m in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
    python make_stats.py -s $op --interval $iv -m $m >& /dev/null &
done

exit

python make_stats.py -s $op --interval $iv CLMcom
python make_stats.py -s $op --interval $iv CLMcom-BTU
python make_stats.py -s $op --interval $iv CLMcom-ETH
python make_stats.py -s $op --interval $iv CNRM
python make_stats.py -s $op --interval $iv DMI
python make_stats.py -s $op --interval $iv GERICS
python make_stats.py -s $op --interval $iv ICTP
python make_stats.py -s $op --interval $iv IPSL
python make_stats.py -s $op --interval $iv KNMI
python make_stats.py -s $op --interval $iv MOHC
python make_stats.py -s $op --interval $iv MPI-CSC
python make_stats.py -s $op --interval $iv RMIB-UGent
python make_stats.py -s $op --interval $iv SMHI
python make_stats.py -s $op --interval $iv UHOH
