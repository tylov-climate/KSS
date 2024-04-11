#!/usr/bin/env python
#
# Coded by Tyge Lovset, Feb/March 2024

import os
import sys
import glob
import cartopy
import shutil
import platform

# EUR-11 Cordex data.

eur_rpole = ((-28.375, -23.375), (18.155, 21.835)) # lon-lat
nor_rpole = ((-6.595, 7.535), (4.735, 20.625))     # lon-lat
nor_lonlat = ((5.684921607269574, 57.73557430824275), (31.682012795900178, 70.93623338069854))


# Around 95% of models are in rotated_pole projection, rlat=412 x rlon=424 grid
#   rotated_pole:grid_north_pole_latitude = 39.25 ;
#   rotated_pole:grid_north_pole_longitude = -162. ;
# and cropped to Norway to 124 x 108.
# The rest of the models are in different projections and grid sizes, so we create
# a griddes.txt file using 'cdo griddes cropped_rotated_pole.nc > griddes.txt'
# and then 'cdo remapbil,griddes.txt in.nc out.nc' to convert and crop when
# input is not rotated_pole 412 x 424 grid.

# The following models have different grid types:
# (Note that some values in ALADIN53 models have TAS in C, although units=K. Is handled in analysis).

# Lambert conformal: 453 x 453 grid:
# CNRM/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALADIN63/v2
# CNRM/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALADIN53/v1
# CNRM/MPI-M-MPI-ESM-LR/(hist,rcp85)/r1i1p1/ALADIN63/v2
# CNRM/MOHC-HadGEM2-ES/(hist,rcp85)/r1i1p1/ALADIN63/v1

# Lambert conformal: 485 x 485 grid:
# RMIB-UGent/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALARO-0

# Lambert conformal: 527 x 527  grid:
# ICTP/MPI-M-MPI-ESM-LR/(hist,rcp26,rcp85)/r1i1p1/RegCM4-6/v1
# ICTP/MOHC-HadGEM2-ES/(hist,rcp26,rcp85)/r1i1p1/RegCM4-6/v1

class Projection:
    def __init__(self):
        self.pcarr = cartopy.crs.PlateCarree()
        self.rpole = cartopy.crs.RotatedPole(pole_latitude=39.25, pole_longitude=-162.0)

    def rotpole_to_lonlat(self, p):
        return self.pcarr.transform_point(p[0], p[1], self.rpole)

    def lonlat_to_rotpole(self, p):
        return self.rpole.transform_point(p[0], p[1], self.pcarr)


def crop_cordex_eur11_to_norway(inroot, outroot):
    proj = Projection()
    p = proj.lonlat_to_rotpole(nor_lonlat[0])
    q = proj.lonlat_to_rotpole(nor_lonlat[1])
    print('Rotated pole lon:',(p[0],q[0]), 'lat:',(p[1],q[1]))

    # Rather use fixed pixels p=lower left, q=upper right
    p = (196, 279)
    q = (303, 402)

    if inroot[-1] != '/':
        inroot += '/'

    pattern = os.path.join(inroot, args.model);
    print(pattern)
    for mpath in glob.glob(pattern):
        model = os.path.basename(mpath)
        for root, dirs, files in os.walk(mpath):
            if args.cmip == '5':
                if not ('/CNRM-ESM2-1/' in root or '/HCLIMcom-METNo/' in root):
                    continue
            if args.cmip == '6':
                if not '/day/' in root:
                   continue
            for f in files:
                if f.endswith('.nc') and (f.startswith('tas_') or f.startswith('pr_')):
                    infile = os.path.join(root, f)
                    subpath = root.replace(inroot, '')
                    outdir = os.path.join(outroot, subpath)
                    outfile = os.path.join(outdir, f)
                    print(f)
                    if os.path.isfile(outfile) and os.path.getmtime(outfile) > os.path.getmtime(infile):
                        continue

                    print('Path:', subpath, file=sys.stderr)
                    print('     ', f, file=sys.stderr)

                    # Crop bounding box of Norway with accurate fixed pixels (integer args are interpreted as pixels, not lon,lat values!)
                    #ret = os.system('ncks -d rlon,%d,%d -d rlat,%d,%d %s -O %s' % (p[0],q[0], p[1],q[1], infile, 'tmp.nc'))

                    #ret = os.system('cdo selindexbox,%d,%d,%d,%d %s %s' % (p[0],q[0], p[1],q[1], infile, 'tmp.nc'))
                    #print("ret is", ret)
                    #if ret != 0:
                    if True:
                        # Probably not "standard" rotated_pole 412x424 grid, so try with combined bi-linear remapping and crop instead:
                        print(f'cdo -z zip_2 remapbil,griddes.txt {infile} tmp-{f}')
                        ret = os.system(f'cdo -z zip_2 remapbil,griddes.txt {infile} tmp-{f}')

                    if ret == 0:
                        if not os.path.isdir(outdir):
                            os.makedirs(outdir)
                        shutil.move(f'tmp-{f}', outfile)
                    else:
                        print('Result:', ret, file=sys.stderr)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('extract_norway.py - extract norway from cordex data')
    print('')

    parser.add_argument(
        '--cmip',  default='5',
        help='CMIP (5=default, 6)'
    )
    parser.add_argument(
        '-m', '--model', default='*',
        help='Select model (default "*")'
    )
    parser.add_argument(
        '-v', '--variable', default='*',
        help='Select variable (default "*")'
    )
    return parser.parse_args()

# MAIN

if __name__ == '__main__':
    args = parse_args()
    uname = platform.uname()

    if 'ppi-ext' in uname.node: # ppi-ext-login.met.no
        if args.cmip == '5':
            inroot = "/lustre/storeC-ext/users/kin2100/MET/cordex/output/EUR-11"
            outroot = "/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway/EUR-11-CMIP5"
        elif args.cmip == '6':
            #inroot = "/lustre/storeC-ext/users/kin2100/MET/cordex/CMIP6/RCM/NOR-12" #KNMI
            inroot = "/lustre/storeC-ext/users/kin2100/MET/cordex/CMIP6/RCM/EUR-11"
            outroot = "/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway/EUR-11-CMIP6"
    elif '-nird' in uname.node: # login.nird.sigma2.no
        if args.cmip == '5':
            print("No input data available on NIRD")
            exit()
        elif args.cmip == '6':
            inroot = '/projects/NS9001K/tylo/DATA/cordex/NOR-12' # KNMI
            outroot = '/projects/NS9001K/tylo/DATA/cordex-norway/EUR-11-CMIP6'

    print(uname.node, args.cmip)
    print("inroot:", inroot)
    print("outroot:", outroot)
    crop_cordex_eur11_to_norway(inroot, outroot)
