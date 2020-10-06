import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df_kss = None

def plot1_all_seasons(df):
    markers = ['o', 'v', 'd', '^', 'D', 'v', 'o', 'd', 'v', 'v', 'v', '^', 'v']
    df_kss = df
    #df[df.Season == 'spring']
    g = sns.FacetGrid(df_kss, col='Season', row='Period', hue='Experiment', palette='bright') # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', markers=markers, style='Previous Study')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(570, 1570), ylim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(585, 1608), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')
    plt.show()


def period_diff_plt(x, y, style, **kwargs):
    xm, ym = np.mean(x), np.mean(y)
    # Average, big diamond:
    c = kwargs.get('color', 'k')
    plt.scatter(x=xm, y=ym, color=c, marker='D', s=60)
    ax = sns.scatterplot(x, y, s=20, **kwargs)
    #ax.axhline(ym, alpha=0.5, color='grey')
    #ax.axvline(xm, alpha=0.5, color='grey')
    #index = kwargs.get('index', 'k')
    #print(style.iloc[1], type(style.iloc[1]))
    x = x.to_numpy()
    y = y.to_numpy()
    if c[2] == 1.0:
        list = np.unique([np.where(x == max(x)), np.where(y == max(y)), np.where(x == min(x)), np.where(y == min(y))])
    else:
        list = []
    for i in list:
        ax.text(x[i], y[i], style.iloc[i], size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')


def plot1_diff(df, season='annual'):
    markers = ['v', 'o']
    global df_kss
    df = df[df.Season == season]
    df = df[df.Experiment != 'historical']
    df_kss = df
    g = sns.FacetGrid(df_kss, col='Experiment', row='Period', hue='Previous Study', palette='bright') # height=6, aspect=.8
    g.fig.suptitle('Precipitation vs Temperature - %s' % season, fontsize=16, y=1.0)
    g.map(period_diff_plt, 'PR diff', 'TAS diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.set_axis_labels('Precipitation diff. mm.', 'Surface Temp. diff. C.')
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.add_legend()
    #plt.show()


def plot2(df):
    markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    df_kss = df[df.Season == 'annual']
    g = sns.FacetGrid(df_kss, row='Previous Study', col='Period', hue='Experiment', palette='bright') # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', style='Institute', markers=markers, legend='full')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    #g.set_titles(col_template="{col_name} patrons", row_template="{row_name}")
    g.set(xlim=(2, 3.8), ylim=(-3, 9)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.set(xlim=(585, 1608), ylim=(8, 19)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')
    #plt.show()


def test():
    sns.set(style='ticks')
    exercise = sns.load_dataset('exercise')
    print(exercise)
    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
    print (df1)
    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
    df2 = None
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])
    plt.show()


if __name__ == '__main__':
    # Read dataset
    #df = pd.read_csv('kss_analysis_v2.csv', index_col=0, sep=';')
    df = pd.read_pickle('kss_analysis_v2.pkl')
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['Full Model'] = models

    #sns.set_style('whitegrid')
    sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
    #plot1_all_seasons(df)
    plot1_diff(df)
    '''
    plot1_diff(df, 'spring')
    plot1_diff(df, 'summer')
    plot1_diff(df, 'autumn')
    plot1_diff(df, 'winter')
    '''
    plt.show()
