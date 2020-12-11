def diff_mean_test(df1, df2, col, size=10000):
    
    """Calculates the probability of a mean difference at least as large as the observed 
    difference assuming the null hypothesis."""
    
    #drop na values and compute averages
    arr1 = df1[col].dropna()
    arr2 = df2[col].dropna()
    arr1_mean = np.sum(arr1) / len(arr1)
    arr2_mean = np.sum(arr2) / len(arr2)
    avg_mean = (arr1_mean + arr2_mean) / 2
    mean_diff = arr1_mean - arr2_mean
    #shift arrays to have same average mean
    arr1_shift = arr1 - arr1_mean + avg_mean
    arr2_shift = arr2 - arr2_mean + avg_mean
    #bootstrap shifted arrays
    bs1 = bs_samples(arr1_shift, size=size)
    bs2 = bs_samples(arr2_shift, size=size)
    #calculate p value
    bs_diff = bs1 - bs2
    pval = np.sum(np.abs(bs_diff) >= np.abs(mean_diff)) / len(bs_diff)
    
    print('Difference in observed means is', 
          str(mean_diff) + '. The probability of observing this difference under the null hypothesis is', 
          str(pval * 100) + '%.')
    
    return pval




def timelag(df, col1, col2, datecol='Date', retdates=False):
    
    """Calculates the time lag between the maxes of two columns, col1 and col2 over each year.
    Returns a list of time deltas, one for each year. Dataframe must have a datetime column datecol."""
    
    dates = []
    deltat = []
    for year in df.Date.dt.year.unique():
        selection1 = df.loc[(df.Date.dt.year == year) & ~df[col1].isnull(), col1]
        selection2 = df.loc[(df.Date.dt.year == year) & ~df[col2].isnull(),  col2]
        if len(selection1) > 0 and len(selection2) > 0:
            idxmaxcol1 = selection1.idxmax()
            date1 = df.loc[idxmaxcol1, datecol]
            idxmaxcol2 = selection2.idxmax()
            date2 = df.loc[idxmaxcol2, datecol]
            dates.append((date1, date2))
            deltat.append(date2 - date1)
    if retdates:
        return dates, deltat
    else:
        return deltat