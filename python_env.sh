# conda
# Put folling in ~/.basrc:
#  $ source /cluster/software/Anaconda3/etc/profile.d/conda.sh
#  $ conda activate kin2100
# Check out https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

# conda create -y -n kin2100 python=3.9
# conda activate kin2100
pip install basemap
conda install -y -c conda-forge cartopy
#conda install -y -c conda-forge nco
#conda install -y -c conda-forge cdo # nird-lmd has v2.1.0
conda install -y -c conda-forge gsl
conda install -y -c conda-forge netCDF4 xarray
conda install -y -c conda-forge pandas
conda install -y -c conda-forge matplotlib
conda install -y -c conda-forge seaborn
conda install -y -c conda-forge ncview
