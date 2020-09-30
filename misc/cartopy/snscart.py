#!/usr/bin/env python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import cartopy.crs
import cartopy.feature


df = pd.read_table('https://gist.githubusercontent.com/shoyer/9698df62662ca7243180/raw/'
                   'c9d45b7c9acb3a47341cc8510415887f1b8f5e28/urbanareas1_1.tsv')
df = pd.melt(df, id_vars=['City', 'City_Alternate', 'Country', 'Latitude', 'Longitude', 'Country_ISO3'],
             value_name='Population')
df['Year'] = df['variable'].str.slice(3, 7).astype(int)
df['PopulationCategory'] = pd.cut(df['Population'], [0, 1000, 2000, 3000, 5000, 100000], right=False)

def scatterplot(x, y, s, color=None, **kwargs):
    # the default plt.scatter handles size scaling poorly, so we define our own
    # see also: https://github.com/mwaskom/seaborn/issues/315
    scaled_size = 0.005 * s
    plt.scatter(x, y, s=scaled_size, edgecolor=color, facecolor='none', linewidth=1, **kwargs)

g = sns.FacetGrid(df[df['Year'] % 25 == 0], col="Year", hue='PopulationCategory',
                  col_wrap=2, height=3.5, aspect=2, palette=sns.dark_palette('Red', 5),
                  subplot_kws=dict(projection=cartopy.crs.Mollweide()))
g.map(scatterplot, "Longitude", "Latitude", "Population",
      transform=cartopy.crs.PlateCarree(), zorder=10)
for ax in g.axes.ravel():
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS)
    ax.set_global()

plt.show()