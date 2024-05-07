save=--save

for c in 5 6 ; do 
    for s in MAM JJA SON DJF ; do # ANN 

        for v in "TAS" "PR" ; do
            python plot_kss.py --cmip $c -P kde1 -v "$v" -s $s $save
        done

        for p in 1 2 3 4; do
            echo python plot_kss.py --cmip $c -P scatter -p $p -s $s $save
            for v in "TAS" "PR" ; do
                echo ABS "$v" $p $s
                python plot_kss.py --cmip $c -P bar -v "$v" -p $p -s $s $save
                python plot_kss.py --cmip $c -P kde2 -v "$v" -p $p -s $s $save
                #python plot_kss.py --cmip $c -P cat1 -v "$v" -p $p -s $s --abs $save
                #python plot_kss.py --cmip $c -P cat2 -v "$v" -p $p -s $s --abs $save
            done
        done

        #for p in 3 4 ; do
        #    echo DIFF "$v" $p $s
        #    python plot_kss.py --cmip $c -P scatter -v "$v" -p $p -s $s $save
        #    python plot_kss.py --cmip $c -P scatter -v "$v" -p $p -s $s $save
        #    python plot_kss.py --cmip $c -P bar -v "$v" -p $p -s $s $save
        #    #python plot_kss.py --cmip $c -P cat1 -v "$v" -p $p -s $s $save
        #    #python plot_kss.py --cmip $c -P cat2 -v "$v" -p $p -s $s $save
        #done
    done
    
    #for p in 1 2 ; do
    #    echo GEO DIFF "$v" $p
    #    echo python plot_kss.py --cmip $c -P geo -v "$v" -p $p $save
    #done
    #for p in 0 1 2 ; do
    #    echo GEO ABS "$v" $p
    #    echo python plot_kss.py --cmip $c -P geo -v "$v" -p $p --abs $save
    #done
done
