#!/usr/bin/env python
#
# Coded by Tyge Lovset, Oct 2020

import os
import sys
import glob
import platform

# seNorge2018.


def senorge2018_to_eur11(inroot, outdir):
    if inroot[-1] != '/':
        inroot += '/'
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for infile in glob.glob(os.path.join(inroot, '*.nc')):
        base = os.path.basename(infile)
        outfile = os.path.join(outdir, base)
        if not os.path.isfile(outfile):
            ret = os.system('cdo remapbil,griddes.txt %s %s' % (infile, 'tmp.nc'))
            if ret == 0:
                os.rename('tmp.nc', outfile)
            else:
                print('Result:', ret, file=sys.stderr)
        else:
            pass
            #print('Exists')

# MAIN

if __name__ == '__main__':
    uname = platform.uname()
    if uname[0] != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if uname[1] == 'DESKTOP-H8NNHQA': # Home PC.
        inroot = '/mnt/j/DATA/seNorge2018'
        outdir = '/mnt/c/Dev/DATA/cordex-norway/seNorge2018'
    else:
        print('Exit. Configured paths for home PC only.')
        exit()
    senorge2018_to_eur11(inroot, outdir)
