import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Read dataset
df = pd.read_csv('kss_analysis.csv', index_col=0)
#df = pd.read_pickle('kss_analysis.pkl')
#print(df.head())

previous_models = np.array([
    ['ICHEC−EC−EARTH', 'r3i1p1',  'HIRHAM5'],
    ['ICHEC−EC−EARTH', 'r12i1p1', 'RCA4'],
    ['ICHEC−EC−EARTH', 'r12i1p1', 'CCLM4−8−17'],
    ['ICHEC−EC−EARTH', 'r1i1p1',  'RACMO22E'],
    ['CERFACS−CNRM−CM5', 'r1i1p1',  'RCA4'],
    ['CERFACS−CNRM−CM5', 'r1i1p1',  'CCLM4−8−17'],
    ['IPSL−CM5A−MR', 'r1i1p1',  'RCA4'],
    ['IPSL−CM5A−MR', 'r1i1p1',  'WRF331F'],
    ['MPI−ESM−LR', 'r1i1p1',  'REMO2009'],
    ['MPI−ESM−LR', 'r1i1p1',  'RCA4'],
    ['MPI−ESM−LR', 'r1i1p1',  'CCLM4−8−17'],
    ['MOHC−HadGEM2−ES', 'r1i1p1',  'RCA4'],
]).T

# Recommended way
#sns.lmplot(x='Attack', y='Defense', data=df)

#sns.set_style("ticks")
sns.set_style('whitegrid')
#markers = df['Model'] == previous_models[0][0]

marker = ['s', 'd', '^', 'D', 'v', 'o', 'v', 'v', 'v', 'v', '^', 'v']
markers = [marker[i] for i in range(len(df["Institute"].unique()))]

#df['markers'] = markers
g = sns.FacetGrid(df[df.Season == 'spring'], row='Season', col='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
g.map_dataframe(sns.scatterplot, x='PR mm.day', y='TAS celsius', style='Institute', markers=markers)
g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
g.add_legend()
#g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
g.set(xlim=(1.6, 4.4), ylim=(-10, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
#g.set(xlim=(1.6, 4.4), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
#g.savefig("facet_plot.png")

'''
sns.lmplot(x='PR mm.day', y='TAS celsius', data=df,
           fit_reg=False, # No regression line
           hue='Season',  # Color by evolution stage
           palette = "husl")
'''
# Tweak using Matplotlib
#plt.ylim(0, None)
#plt.xlim(0, None)
plt.show()
exit()

#fig = plt.figure()
#sns.boxplot(data=df)

fig = plt.figure()
# Pre-format DataFrame
stats_df = df.drop(['Total', 'Stage', 'Legendary'], axis=1)
# New boxplot using stats_df
sns.boxplot(data=stats_df)

# Melt DataFrame
melted_df = pd.melt(stats_df,
                    id_vars=["Name", "Type 1", "Type 2"], # Variables to keep
                    var_name="Stat") # Name of melted variable
print(melted_df)


#fig = plt.figure()
# Set theme
#sns.set_style('whitegrid')
# Violin plot
#sns.violinplot(x='Type 1', y='Attack', data=df)



# Set figure size with matplotlib
plt.figure(figsize=(10,6))
sns.set_style('whitegrid')
# Create plot
sns.violinplot(x='Type 1',
               y='Attack',
               data=df,
               inner=None, # Remove the bars inside the violins
               )

sns.swarmplot(x='Type 1',
              y='Attack',
              data=df,
              color='k', # Make points black
              alpha=0.7) # and slightly transparent

# Set title with matplotlib
plt.title('Attack by Type')


plt.show()