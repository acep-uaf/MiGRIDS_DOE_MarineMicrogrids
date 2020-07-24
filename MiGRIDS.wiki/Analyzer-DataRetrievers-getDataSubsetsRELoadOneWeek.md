Selects datasubsets based on RE penetration levels and load levels. It searches for the weeks with min, mean, and max absolute RE levels, and for min, mean, and max load levels.

# Inputs
**dataframe**: [Dataframe] contains full time-series of necessary model input channels

**otherInputs**: [list(str)] bin for additional parameters for implemented method. Currently not used.

# Outputs
**datasubsets**: [Dataframe of dataframes] the subsets of timeseries for all input channels required to run the model organized depending on method of extraction.

**databins**: [DataFrame] provides weights each data frame in datasubsets should be given when extrapolating results. This dataframe has two columns of the same length as the original time series. Column 'loadBins' contains the binning based on average load (min = 1, mean = 2, max = 3), column 'varGenBins' does the same for the variable generation dimension.