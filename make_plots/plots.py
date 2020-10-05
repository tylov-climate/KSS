import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def compute_deltas(df):
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])


def plot1_all_seasons(df):
    markers = ['o', 'v', 'd', '^', 'D', ]  # '^', 'D', 'v', 'o', 'd', 'v', 'v', 'v', '^', 'v']
    #df[df.Season == 'spring']
    g = sns.FacetGrid(df, col='Season', row='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius') # , markers=markers, style='Last Study')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    #g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(570, 1570), ylim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(585, 1608), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig("facet_plot.png")
    plt.show()


def plot1_diffs(df):
    markers = ['o', 'v', 'd', '^', 'D', ]  # '^', 'D', 'v', 'o', 'd', 'v', 'v', 'v', '^', 'v']
    #df[df.Season == 'spring']
    #histo_diff = df[df.Experiment == 'historical']
    rcp26 = df[df.Experiment == 'rcp26'].drop(columns=['Experiment'])
    rcp45 = df[df.Experiment == 'rcp45'].drop(columns=['Experiment'])
    rcp85 = df[df.Experiment == 'rcp85'].drop(columns=['Experiment'])
    print(rcp26['TAS celsius'])
    print(rcp45['TAS celsius'])
    print(rcp85['TAS celsius'])
    exit()

    g = sns.FacetGrid(df, col='Season', row='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', markers=markers) # style='Last Study', 
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(570, 1570), ylim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(585, 1608), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig("facet_plot.png")
    plt.show()



def plot2(df):
    markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    #df[df.Season == 'spring']
    g = sns.FacetGrid(df[df.Season == 'annual'], row='Last Study', col='Period', hue='Experiment', palette="bright") # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', style='Institute', markers=markers, legend='full')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(2, 3.8), ylim=(-3, 9)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(585, 1608), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig("facet_plot.png")
    plt.show()



if __name__ == '__main__':
    # Read dataset
    df = pd.read_csv('kss_analysis_v2.csv', index_col=0, sep=';')
    #df = pd.read_pickle('kss_analysis_v2.pkl')
    #print(df.head())
    #add_last_study_column(df)
    plot1_all_seasons(df)
