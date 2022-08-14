#!/bin/bash

save=--save


for v in "TAS diff" "PR diff"
do
    for s in ANN MAM JJA SON DJF
    do
        for t in 1 2
        do
            echo DIFF "$v" $t $s
            python plot_kss.py -p scatter -v "$v" -t $t -s $s $save
            python plot_kss.py -p bar -v "$v" -t $t -s $s $save
            python plot_kss.py -p bar -v "$v" -t $t -s $s --overlap $save
            python plot_kss.py -p cat1 -v "$v" -t $t -s $s $save
            python plot_kss.py -p cat2 -v "$v" -t $t -s $s $save
        done
        for t in 0 1 2
        do
            echo ABS "$v" $t $s
            python plot_kss.py -p scatter -v "$v" -t $t -s $s --abs $save
            python plot_kss.py -p bar -v "$v" -t $t -s $s --abs $save
            python plot_kss.py -p bar -v "$v" -t $t -s $s --overlap --abs $save
            python plot_kss.py -p cat1 -v "$v" -t $t -s $s --abs $save
            python plot_kss.py -p cat2 -v "$v" -t $t -s $s --abs $save
        done
    done
    for t in 1 2
    do
        echo GEO DIFF "$v" $t
        python plot_kss.py -p geo -v "$v" -t $t $save
    done
    for t in 0 1 2
    do
        echo GEO ABS "$v" $t
        python plot_kss.py -p geo -v "$v" -t $t --abs $save
    done    
done

