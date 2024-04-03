#op=mean --ensemble
#if [ ! -z $1 ]; then op=$1; fi

n=0
nthreads=4

if [ 1 == 1 ]; then
    for iv in yseas ymon; do
        for op in mean max min; do

            echo "generate log files for $iv$op"
            for t in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
                echo start $t
                python make_cmip5_stats.py --dry -s $op --selected --interval $iv -t $t > logs/$t-$iv$op-selected.log
            done

            echo "run $iv$op stats the background"
            for t in CLMcom CLMcom-BTU CLMcom-ETH CNRM DMI GERICS ICTP IPSL KNMI MOHC MPI-CSC RMIB-UGent SMHI UHOH; do
                while :; do
            	    if [ $(jobs -p|wc -l) -lt $nthreads ]; then
                        ((n++))
                        echo "start $n: $t-$iv$op"
                        python make_cmip5_stats.py -s $op --selected --interval $iv -t $t >& /dev/null &
                        break
                    fi
                    sleep 0.5s
                done
            done
        done
    done
fi

exit

iv=yseas
op=mean

python make_stats.py -s $op --interval $iv -t CLMcom
python make_stats.py -s $op --interval $iv -t CLMcom-BTU
python make_stats.py -s $op --interval $iv -t CLMcom-ETH
python make_stats.py -s $op --interval $iv -t CNRM
python make_stats.py -s $op --interval $iv -t DMI
python make_stats.py -s $op --interval $iv -t GERICS
python make_stats.py -s $op --interval $iv -t ICTP
python make_stats.py -s $op --interval $iv -t IPSL
python make_stats.py -s $op --interval $iv -t KNMI
python make_stats.py -s $op --interval $iv -t MOHC
python make_stats.py -s $op --interval $iv -t MPI-CSC
python make_stats.py -s $op --interval $iv -t RMIB-UGent
python make_stats.py -s $op --interval $iv -t SMHI
python make_stats.py -s $op --interval $iv -t UHOH
