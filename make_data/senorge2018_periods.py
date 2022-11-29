#!/usr/bin/env python
#
# Coded by Tyge Lovset, Oct 2020

import os
import sys
import glob
import platform

# seNorge2018.


def senorge2018_periods(inroot, outroot):
    if inroot[-1] != '/':
        inroot += '/'

    for per in periods:
        for ival in intervals:
            for var in variables:
                for op in operators:
                    outdir = '%s_%s%s_%d-%d_histo' % (var, ival, op, per[0], per[1])
                    outfolder = os.path.join(outroot, outdir)
                    if not os.path.isdir(outfolder):
                        os.makedirs(outfolder)
                    files = []
                    for y in range(per[0], per[1]+1):
                        file = os.path.join(inroot, '%s_seNorge2018_%d_remap.nc' % (var, y))
                        files.append(file)
                    outbase = '%s_EUR-11_seNorge_seNorge2018_historical_r1i1p1_None_v1_%s%s_v20190101_%d-%d.nc' % (var, ival, op, per[0], per[1])
                    outfile = os.path.join(outfolder, outbase)
                    cmd = "cdo -L %s%s -cat '%s' %s" % (ival, op, ' '.join(files), outfile)
                    print(cmd)
                    ret = os.system(cmd)
                    print('')

# MAIN

periods = ((1971, 2000), (1985, 2014), (1991, 2020)) # , (2041, 2070), (2071, 2100)) # 5+6
intervals = ('yseas', 'ymon')
operators = ('mean', 'max') # , 'min', 'std')
variables = ('pr', 'tas') # , 'min', 'std')

if __name__ == '__main__':
    uname = platform.uname()
    if uname[0] != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if uname[1] == 'DESKTOP-H8NNHQA': # Home PC.
        inroot = '/mnt/j/DATA/seNorge2018'
        outroot = '/mnt/c/Dev/DATA/cordex-norway/seNorge2018'
    else:
        inroot = 'out'
        outroot = 'stats_v3'
        #print('Exit. Configured paths for home PC only.')
        #exit()

    senorge2018_periods(inroot, outroot)
