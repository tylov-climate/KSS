import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

def facetgrid_all(df):
    #df = df[df.Season == 'ANN']
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Season', # col_order= ('ANN', 'JJA', 'SON'),
                          row='Period', row_order=('2071-2100', '2031-2060', '1951-2000'),
                          hue='Experiment', hue_order=('historical', 'rcp45'), palette='bright', height=3.6, aspect=1.0)
    g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year') # , markers=markers, style='Experiment')
    #g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.92, left=0.04, bottom=0.07)
    g.fig.suptitle('Nedbør og temperatur for fastlands-norge (absoluttverdier)', fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    g.set(ylim=(570, 1620), xlim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')


def scatterplot_func(x, y, style, **kwargs):
    xm, ym = np.mean(x), np.mean(y)
    # Average, big diamond:
    c = kwargs.get('color', 'k')
    plt.scatter(x=xm, y=ym, color=c, marker='D', s=60)
    ax = sns.scatterplot(x, y, s=25, marker='o', **kwargs)
    ax.axhline(ym, alpha=0.1, color='black')
    ax.axvline(xm, alpha=0.1, color='black')
    x = x.to_numpy()
    y = y.to_numpy()
    if c[2] == 1.0:
        list = np.unique((np.where(x == max(x)), np.where(y == max(y)), np.where(x == min(x)), np.where(y == min(y))))
    else:
        list = np.unique(np.where(y == max(y))) # Old models: print high precipitation only
    for i in list:
        p = style.iloc[i].split('_', 2)
        s = '-'.join(p[0].split('-')[:2] + p[1:])
        ax.text(x[i], y[i], s, size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')


def facetgrid_differences(df, season='ANN'):
    markers = ['v', 'o']
    #sns.set_style('whitegrid')
    sns.set(style='ticks')
    df = df[df.Season == season]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment', row='Period', row_order=('2071-2100', '2031-2060'),
                          hue='Previous Study', palette='bright', height=5, aspect=1.0,
                          legend_out=True, despine=False, sharex=False, sharey=False) #
    g.fig.suptitle('Nedbør- og temperatur-endring: %s' % season, fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.90, wspace=0.2)
    g.set_axis_labels('Temperaturendring [°C]', 'Nedbørsendring [%]')
    g.add_legend()


def plot2(df):
    df = df[df.Season == 'ANN']
    g = sns.FacetGrid(df, row='Previous Study', col='Period', hue='Experiment', palette='bright') # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', style='Institute', markers=markers, legend='full')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    g.set(xlim=(2, 3.8), ylim=(-3, 9)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')


def test():
    sns.set(style='ticks')
    exercise = sns.load_dataset('exercise')
    print(exercise)
    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
    print (df1)
    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
    df2 = None
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])


if __name__ == '__main__':
    # Read dataset
    df = pd.read_csv('kss_analysis_v2.csv', index_col=0, sep=';')
    #df = pd.read_pickle('kss_analysis_v2.pkl')

    # Add full model column:
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['Full Model'] = models

    #sns.set_style('whitegrid')
    #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
    #sns.set(style='ticks')
    facetgrid_all(df)
    #facetgrid_differences(df)
    '''
    facetgrid_differences(df, 'MAM')
    facetgrid_differences(df, 'JJA')
    facetgrid_differences(df, 'SON')
    facetgrid_differences(df, 'DJF')
    '''
    plt.show()
