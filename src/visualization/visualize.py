from folium import Map, Marker, Icon
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



def resampled_counts(df, datecol, resample='M', cols=None, figsize=(15,3),
                       title=None, width=15, alpha=0.5, subplots=False, fcn='count'):
    
    ''' Resamples a dataframe over a given timeframe, and plots counts of the columns as 
    overlapping bar charts. The datecol input must contain datetimes. The cols parameter 
    should be a list of columns. Can aggregate using a different function by setting the fcn parameter'''
    
    dfc = df.resample(resample, on=datecol).agg(fcn)
    idx = dfc.index
    if cols == None:
        cols = df.columns
    fig, ax = plt.subplots(figsize=figsize)
    for i, col in enumerate(cols):
        ax.bar(idx, dfc[col], width=width, alpha=alpha, label=col, 
               color='C{0}'.format(i))
    ax.xaxis_date()
    ax.set_xlabel('Date')
    ax.set_ylabel('Measurement Counts')
    ax.legend(loc='best')
    ax.set_title(title)



def mapsites(df, col=None):
    
    """Maps site measurements and labels them by site name and date. If a numeric column name is optionally entered then the
      icons will be color coded according to value quartile, with green as the lowest quartile up to dark red as the top
      quartile."""
    
    m = Map(location=[41.76, -83.26])
    if col:
        crange = df[col].describe()
    for i in df.index:
        lat = df.loc[i, 'Latitude (decimal deg)']
        long = df.loc[i, 'Longitude (decimal deg)']
        site = df.loc[i,'Site']
        date = df.loc[i, 'Date']

        if col:
            val = df.loc[i, col]
            if val <= crange['25%']:
                color = 'green'
            elif val <= crange['50%']:
                color = 'orange'
            elif val <= crange['75%']:
                color = 'red'
            else:
                color = 'darkred'
            Marker([lat, long], popup=(lat,long), tooltip=(site, date), icon=Icon(color=color)).add_to(m)
        else:
            Marker([lat, long], popup=(lat,long), tooltip=(site, date)).add_to(m)
            
    return m




def timeplot(df, cols, datecol='Date', logy=False, squish=False, title=None):
    
    """Plots columns in a dataframe with a DateTime column as subplots with the DateTime as the x-axis. The DateTime
    column is assumed to be named 'Date' or can be entered as an input. Columns should be in list format, and 
    the y-axis can optionally be plotted on a log scale by setting logy=True. If the squish option is set to True
    then the Dates will be processed as strings, removing proper date scaling on the x-axis by removing Dates with 
    null values in all columns."""
    
    #insert dummy NaNs for January months to prevent linear interpolation from year to year
    years = df.Date.dt.year.unique()
    null = pd.DataFrame(data={'Date': [pd.to_datetime('{0}-01-01'.format(y)) for y in years]})
    temp = df.append(null).sort_values(datecol)
    
    if not squish:
        #years = df.Date.dt.year.unique()
        #null = pd.DataFrame(data={'Date': [pd.to_datetime('{0}-01-01'.format(y)) for y in years]})
        #temp = df.append(null).sort_values(datecol)
        temp.plot(x=datecol, y=cols, subplots=True, marker='.', logy=logy, figsize=(15, len(cols)*4), title=title)
        
    if squish:
        temp['DateString'] = temp[datecol].astype('str')
        temp.plot(x='DateString', y=cols, subplots=True, marker='.', logy=logy, figsize=(15, len(cols)*4), title=title)
        

        
def ecdf(df, col):
    
    """Returns x and y data for an ECDF of a dataframe column."""
    
    x_data = np.sort(df[col].dropna())
    y_data = np.arange(1, len(x_data) + 1) / len(x_data)
    return x_data, y_data




def comp_ecdf(df1, df2, col, name1='df1', name2='df2'):
    
    """Compares the ECDF of a common column in two different data frames."""
    
    x_1, y_1 = ecdf(df1, col)
    x_2, y_2 = ecdf(df2, col)
    plt.plot(x_1, y_1, marker='.', linestyle=None, label=name1)
    plt.plot(x_2, y_2, marker='.', linestyle=None, label=name2)
    plt.xlabel(col)
    plt.ylabel('ECDF')
    plt.legend()
    plt.show()
    
    
    
def bs_samples(array, size=10000):
    
    """Generates a bootstrapped sample of a given size"""
    
    bs = np.empty(size)
    for i in range(size):
        bs[i] = np.sum(np.random.choice(array, size=len(array))) / len(array)
    return bs


def bs_hist(df1, df2, col, name1='df1', name2='df2'):
    
    """Plots a histogram of bootstrapped means for a shared column in two different dataframes. 
    Also returns confidence intervals for the bootstrapped means."""
    
    #get bootstrapped samples
    array1 = df1[col].dropna()
    array2 = df2[col].dropna()
    df1_bs = bs_samples(array1)
    df2_bs = bs_samples(array2)
    #plot histogram
    plt.hist(df1_bs, label=name1)
    plt.hist(df2_bs, label=name2)
    plt.xlabel('Bootstrapped Means of ' + col)
    plt.ylabel('Counts')
    plt.legend()
    plt.show()
    #print confidence interval
    print('The 95% confidence interval for', name1, col, 'mean is', 
          np.quantile(df1_bs, 0.025), 'to', np.quantile(df1_bs, 0.975))
    print('The 95% confidence interval for', name2, col, 'mean is', 
          np.quantile(df2_bs, 0.025), 'to', np.quantile(df2_bs, 0.975))
    
    
def hist_zoom(df, col, cutoff=None, bins=None):
    
    ''' Displays a histogram of an entire column next to a histogram of all values below a 
    certain cutoff. If no cutoff is specified only the total histogram is shown.'''
    
    if cutoff == None:
        figsize=(15,3)
        plt.hist(df[col], bins=bins)
        plt.title(col)
    else:
        fig, ax = plt.subplots(1, 2, figsize=(15,3))
        ax[0].hist(df[col], bins=bins)
        ax[0].set_title('Total Distribution')
        filter_df = df[df[col] < cutoff]
        ax[1].hist(filter_df[col], bins=bins)
        ax[1].set_title('Partial Distribution - Zoom')
        fig.suptitle(col, fontsize=14)
