# KSS
Norsk Klima Service Senter

To run the python tools in this folder structure, run the command:

source /opt/anaconda3/bin/activate /tos-project4/NS9076K/py38

or put it in your ~/.bash_profile startup file.

You may exit the python environment by running:
deactivate

There are some documentation on how the data is created in the KSS/docs folder.
extract_norway.py make_stats.py and builds the data for analysis in the KSS/make_data folder.

In KSS/make_plots there are make_csv.py, but this need only to be run once to create .csv file for plots.
plot_kss.py can create multiple plots, but some are not very useful yet. The most useful now is:

python plot_kss.py -p diff  # default annual changes relative to ref period.
python plot_kss.py -p diff -s MOM # season
python plot_kss.py -p diff -s JJA -t std # look at changes in standard deviation

This shows a scatter plot with the changes in temperature and presipitation for each of the ensemble members,
relative to historic period. Dimonds are mean values for green (previous study group), and the blue (new).
I have only printed names on the extreme values, and both the IPSL-RCA4 and IPSL-WRF381P are clearly outliers.

python plot_kss.py -p all # absolute values for verification.

The -p all plot seems to have a little low precipitation, but I have tried to verify the data.
Converted from daily kg m-2 s-1 to yearly mm. by multiply by (365.25 * 24 * 60 * 60).

I am working on plots (similar to: plot_kss -p geo) that shows the ensemble spread at each grid point in some ways,
e.g. standard deviation, that will show at which regions in norway where the spread between members is largest.
Also bar-charts that show median, 10, 90 percentile min-max for each of 52 members and variable (pr, tas)

Plots will be saved in the KSS/plots folder, but the file names must be revised.

Shared some info on GITHUB.
