Interface to extractors for short time-series from the overall dataset using a defined method to allow for quicker model runs during searches in the optimization space.

# Inputs
**dataframe**: [Dataframe] contains full time-series of necessary model input channels

**method**: [String] used to define the method for extraction. Currently only 'RE-load-one-week' is implemented.

**otherInputs**: [list(str)] bin for additional parameters for implemented methods.

# Outputs
**datasubsets**: [Dataframe of dataframes] the subsets of timmeseries for all input channels required to run the model organized depending on method of extraction.

**databins**: [DataFrame] provides weights each data frame in datasubsets should be given when extrapolating results. This dataframe has two columns of the same length as the original time series. Column 'loadBins' contains the binning based on average load (min = 1, mean = 2, max = 3), column 'varGenBins' does the same for the variable generation dimension.