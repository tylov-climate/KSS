save=--save

#gcm6="CNRM-ESM2-1 EC-Earth-Consortium-EC-Earth3-Veg EC-Earth3-Veg EC-Earth3 MIROC-MIROC6 MIROC6_HCLIM43 MPI-ESM1-2-HR MPI-M-MPI-ESM1-2-HR NorESM2-MM"
#rcm6="RACMO23E" # CNRM-ESM2-1
gcm6="CNRM-ESM2-1 EC-Earth3-Veg EC-Earth3 MIROC6 MPI-ESM1-2-HR NorESM2-MM"
rcm6="RACMO23E CLMcom-BTU-ICON-2-6-5-rc CLMcom-KIT-CCLM-6-0-clm2 HCLIM43-ALADIN"

python plot_kss.py --cmip 6 -P kde2 -v "PR" --rcm "RACMO23E" -s JJA
exit

#for c in 5 6 ; do
for c in 6 ; do
    #if [ $c == 5 ]; then exp=rcp85; else exp=ssp370; fi

    for s in ANN MAM JJA SON DJF ; do # ANN

        for v in "TAS" "PR" ; do
            python plot_kss.py --cmip $c -P kde1 -v "$v" -s $s $save
            if [ $c == 6 ]; then
                for r in $rcm6; do
                    python plot_kss.py --cmip $c -P kde2 -v "$v" --rcm $r -s $s $save
                done
            fi
        done

        for p in 1 2 3 4; do
            python plot_kss.py --cmip $c -P scatter -p $p -s $s $save

            for v in "TAS" "PR" ; do
                # echo ABS "$v" $p $s
                python plot_kss.py --cmip $c -P bar -v "$v" -p $p -s $s $save
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


"GCM:
----
CNRM-ESM2-1
EC-Earth-Consortium-EC-Earth3-Veg
EC-Earth3-Veg
EC-Earth3
MIROC-MIROC6
MIROC6
MPI-ESM1-2-HR
MPI-M-MPI-ESM1-2-HR
NorESM2-MM

RCM:
----
RACMO23E
CLMcom-BTU-ICON-2-6-5-rc
CLMcom-KIT-CCLM-6-0-clm2
HCLIM43-ALADIN"
