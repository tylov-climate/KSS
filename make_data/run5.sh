#python make_cmip5_stats.py --dry -t DMI -s mean --interval yseas --periods=2,4 --ref-period=2 --all
python make_cmip5_stats.py -s mean -x rcp45 --interval yseas --periods=2,4 --ref-period=2 --outdir=/datalake/NS9001K/tylo/kin2100/stats_cmip5_new
