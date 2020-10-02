#!/usr/bin/env python
#
# Coded by Tyge Lovset, 2020
# Ralf Dösher: Nordic, 3 km, Nordic 12km, Alps 3km. Convectional Permitting

import os
import sys
import glob
import cartopy

# EUR-11 Cordex data.

eur_rpole = ((-28.375, -23.375), (18.155, 21.835)) # lon-lat
nor_rpole = ((-6.595, 7.535), (4.735, 20.625))     # lon-lat
nor_lonlat = ((5.684921607269574, 57.73557430824275), (31.682012795900178, 70.93623338069854))

# Labbert conformal: 453 x 453 grid
# CNRM/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALADIN63/v2
# CNRM/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALADIN53/v1
# CNRM/MPI-M-MPI-ESM-LR/(hist,rcp85)/r1i1p1/ALADIN63/v2
# CNRM/MOHC-HadGEM2-ES/(hist,rcp85)/r1i1p1/ALADIN63/v1

# Lambert conformal: 485 x 485 grid
# RMIB-UGent/CNRM-CERFACS-CNRM-CM5/*/r1i1p1/ALARO-0

# Lambert conformal: 527 x 527: crs:proj4_params = "+proj=lcc +lat_1=30.00 +lat_2=65.00 +lat_0=48.00 +lon_0=9.75 +x_0=-6000. +y_0=-6000. +ellps=sphere +a=6371229. +b=6371229. +units=m +no_defs" ;
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

    # Rather use absolute pixels p=lower left, q=upper right
    p = (196, 279)
    q = (303, 402)

    if inroot[-1] != '/':
        inroot += '/'
    for mpath in glob.glob(os.path.join(inroot, '*')):
        model = os.path.basename(mpath)
        for root, dirs, files in os.walk(mpath):
            for f in files:
                if f.endswith('.nc'):
                    infile = os.path.join(root, f)
                    subpath = root.replace(inroot, '')
                    outdir = os.path.join(outroot, subpath)
                    outfile = os.path.join(outdir, f)
                    if not os.path.isfile(outfile):
                        # Crop bounding box of Norway
                        #ret = os.system('ncks -d rlon,%f,%f -d rlat,%f,%f %s -O %s'
                        print('Path:', subpath, file=sys.stderr)
                        print('     ', f, file=sys.stderr)
                        #ret = os.system('ncks -d rlon,%d,%d -d rlat,%d,%d %s -O %s'
                        #                 % (p[0],q[0], p[1],q[1], infile, 'tmp.nc'))
                        ret = -1
                        if ret != 0:
                            ret = os.system('cdo remapbil,griddes.txt %s %s' % (infile, 'tmp.nc'))
                            
                        if ret == 0:
                            if not os.path.isdir(outdir):
                                os.makedirs(outdir)
                            os.rename('tmp.nc', outfile)
                        else:
                            print('Result:', ret, file=sys.stderr)
                    else:
                        pass
                        #print('Exists')

def sample_test():
    proj = Projection()
    p = proj.lonlat_to_rotpole(nor_lonlat[0])
    q = proj.lonlat_to_rotpoley(nor_lonlat[1])
    print('lon',(p[0],q[0]), 'lat',(p[1],q[1]))
    samples = os.path.join('..', 'sample_data')
    base = '_EUR-11_ICHEC-EC-EARTH_rcp85_r12i1p1_SMHI-RCA4_v1_day_20060101-20101231.nc'
    os.system('ncks -d rlon,%d,%d -d rlat,%d,%d %s -O %s' % (p[0],q[0], p[1],q[1],
        os.path.join(samples, 'eur11', 'tas' + base),
        os.path.join(samples, 'nor11', 'tas' + base)))
    os.system('ncks -d rlon,%d,%d -d rlat,%d,%d %s -O %s' % (p[0],q[0], p[1],q[1],
        os.path.join(samples, 'eur11', 'pr' + base),
        os.path.join(samples, 'nor11', 'pr' + base)))

# MAIN

if __name__ == '__main__':
    #sample_test()
    #if len(sys.argv) == 1:
    #    print('give model group name')
    #    exit()
    #group = sys.argv[1]
    crop_cordex_eur11_to_norway(inroot='/tos-project4/NS9076K/data/cordex/output/EUR-11',
                                outroot='/tos-project4/NS9076K/data/cordex-norway/EUR-11')
