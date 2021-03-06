#!/usr/bin/env python
#
# Coded by Tyge Lovset, Sep/Oct 2020

import os
import sys
import glob
import cartopy

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
                        # Crop bounding box of Norway with computed bounding box
                        #ret = os.system('ncks -d rlon,%f,%f -d rlat,%f,%f %s -O %s' % (p[0],q[0], p[1],q[1], infile, 'tmp.nc'))
                        print('Path:', subpath, file=sys.stderr)
                        print('     ', f, file=sys.stderr)
                        # Crop bounding box of Norway with accurate fixed pixels (integer args are interpreted as pixels, not lon,lat values!)
                        ret = os.system('ncks -d rlon,%d,%d -d rlat,%d,%d %s -O %s' % (p[0],q[0], p[1],q[1], infile, 'tmp.nc'))
                        if ret != 0:
                            # Probably not "standard" rotated_pole 412x424 grid, so try with combined bi-linear remapping and crop instead:
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
