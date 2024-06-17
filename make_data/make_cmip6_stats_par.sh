#op=mean --ensemble
#if [ ! -z $1 ]; then op=$1; fi

#n=0
#nthreads=3

    #for iv in yseas ymon; do
    #    echo "generate log files for $op"
    #    for op in mean max min; do
    #        echo start $t
    #        python make_cmip6_stats.py --dry -s $op --interval $iv -t $t > logs/$t-$iv$op.log
    #    done
    #done

#inst="CLMcom-KIT CLMcom-BTU HCLIMcom-METNo HCLIMcom-SMHI KNMI"
inst="KNMI"
interval="yseas" # "yseas ymon"
operation="mean max min"

for iv in $interval; do
    for op in $operation; do
        if [ "$1" == "-e" ]; then
            python make_cmip6_stats.py -s $op --ensemble --interval $iv
        else
            echo "run $iv$op stats in the background"
            for t in $inst; do
                python make_cmip6_stats.py -s $op --interval $iv -t $t 

                #while :; do
                #    if [ $(jobs -p|wc -l) -lt $nthreads ]; then
                #        ((n++))
                #        echo "start $n: $t-$iv$op"
                #        python make_cmip6_stats.py -s $op --interval $iv -t $t >& /dev/null &
                #        break
                #    fi
                #    sleep 2.0s
                #done
            done
        fi
    done
done
