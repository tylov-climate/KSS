#op=mean --ensemble
#if [ ! -z $1 ]; then op=$1; fi

n=0
nthreads=3

    #for iv in yseas ymon; do
    #    echo "generate log files for $op"
    #    for op in mean max min; do
    #        echo start $t
    #        python make_cmip6_stats.py --dry -s $op --interval $iv -t $t > logs/$t-$iv$op.log
    #    done
    #done

for iv in ymon yseas; do
    echo "run $op stats the background"
    for op in max min; do # mean max min; do
        for t in HCLIMcom-METNo HCLIMcom-SMHI KNMI; do
            while :; do
                if [ $(jobs -p|wc -l) -lt $nthreads ]; then
                    ((n++))
                    echo "start $n: $t-$iv$op"
                    #python make_cmip6_stats.py -s $op --interval $iv -t $t >& /dev/null &
                    python make_cmip6_stats.py -s $op --interval $iv -t $t
                    break
                fi
                sleep 0.5s
            done
        done
    done
done
