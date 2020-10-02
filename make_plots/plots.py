import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def add_last_study_column(df):
    original_models = np.array([
        'ICHEC-EC-EARTH_HIRHAM5_r3i1p1',
        'ICHEC-EC-EARTH_RCA4_r12i1p1',
        'ICHEC-EC-EARTH_CCLM4-8-17_r12i1p1',
        'ICHEC-EC-EARTH_RACMO22E_r1i1p1',
        'CNRM-CERFACS-CNRM-CM5_RCA4_r1i1p1',
        'CNRM-CERFACS-CNRM-CM5_CCLM4-8-17_r1i1p1',
        'IPSL-IPSL-CM5A-MR_RCA4_r1i1p1',
        'IPSL-IPSL-CM5A-MR_WRF331F_r1i1p1',
        'MPI-M-MPI-ESM-LR_REMO2009_r1i1p1',
        'MPI-M-MPI-ESM-LR_RCA4_r1i1p1',
        'MPI-M-MPI-ESM-LR_CCLM4-8-17_r1i1p1',
        'MOHC-HadGEM2-ES_RCA4_r1i1p1',
    ])

    #sns.set_style("ticks")
    sns.set_style('whitegrid')
    
    full_mods = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    last_study = full_mods == original_models[0]
    for i in range(1, len(original_models)):
        last_study |= full_mods == original_models[i]
    df['Last Study'] = last_study
    
    #for i in range(len(last_study)):
    #    print(full_mods[i], last_study[i])

    #comb_period = df[df.columns[1:3]].apply(
    #    lambda x: '_'.join(x.dropna().astype(str)),
    #    axis=1
    #)    
    #df['Combined Period'] = comb_period



def plot1(df):
    markers = ['o', 'v', 'd', '^', 'D', ]  # '^', 'D', 'v', 'o', 'd', 'v', 'v', 'v', '^', 'v']
    #df[df.Season == 'spring']
    g = sns.FacetGrid(df, col='Season', row='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.day', y='TAS celsius', style='Last Study', markers=markers)
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(1.6, 4.4), ylim=(-10, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(1.6, 4.4), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig("facet_plot.png")
    plt.show()


def plot2(df):
    markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    #df[df.Season == 'spring']
    g = sns.FacetGrid(df[df.Season == 'annual'], row='Last Study', col='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.day', y='TAS celsius', style='Institute', markers=markers, legend='full')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(2, 3.8), ylim=(-3, 9)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(1.6, 4.4), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig("facet_plot.png")
    plt.show()



if __name__ == '__main__':
    # Read dataset
    df = pd.read_csv('kss_analysis.csv', index_col=0)
    #df = pd.read_pickle('kss_analysis.pkl')
    #print(df.head())
    #add_last_study_column(df)
    plot2(df)
