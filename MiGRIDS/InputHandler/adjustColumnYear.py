# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 1/23/2018
import pandas as pd
import numpy as np

def avg_datetime(series):
    dt_min = series.min()
    dt_max = series.max()
    #return dt_min + np.sum((series - dt_min) / len(series))
    return (dt_max-dt_min)/2 + dt_min

def adjustColumnYear(df):

    # get mean non-nan date of each column
    meanDate = []
    for idx, col in enumerate(df.columns):
        meanDate = meanDate + [avg_datetime(df.index.date[df[col].notnull()])]

    # get the overall mean date
    meanDateOverall = avg_datetime(pd.Series(meanDate))

    # if difference from overall mean date is more than one year, scale by closest number of years

    for idx, col in enumerate(df.columns):

        yearDiff = np.round((meanDate[idx] - meanDateOverall).days / 365)
        # if the difference is greater than a year
        if np.abs(yearDiff) > 0:
            df0 = df[[col]].copy()
            df0.dropna()
            # note that pd.to_timedelta(1,unit='y') is 365 days 05:49:12 .... because of leap years. Need to use days instead
            df0.index = df0.index - pd.to_timedelta(yearDiff*365, unit='d')
            df.drop(col,axis=1,inplace=True)
            df = pd.concat([df, df0], axis=1)
            df.dropna(how = 'all',inplace=True)

    return df