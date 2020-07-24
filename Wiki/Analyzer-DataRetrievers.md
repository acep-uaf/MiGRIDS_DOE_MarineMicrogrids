The package `DataRetrievers` contains routines that retrieve data from simulation input and output data files. Most of these routines are used internally while `plotSetResult` is called by the user to plot simulation results. 
* [getBasecase](Analyzer-DataRetrievers-getBasecase): Retrieves base case data and meta data required for initial estimate of search space boundaries and data sparsing.
* [getComponentTypeData](getComponentTypeData): Retrieves all meta-data for a given component class from the descriptor xml files.
* [getDataChannels](Analyzer-DataRetrievers-getDataChannels): Retrieves data channels based on list of channels requested. ASSUMES that all channels have a uniform time vector.
* [getDataSubsets](Analyzer-DataRetrievers-getDataSubsets):  Interface to extractors for short time-series from the overall dataset using a defined method to allow for quicker model runs during searches in the optimization space.
* [getDataSubsetsRELoadOneWeek](Analyzer-DataRetrievers-getDataSubsetsRELoadOneWeek): Selects data subsets based on RE penetration levels and load levels. It searches for the weeks with min, mean, and max absolute RE levels, and for min, mean, and max load levels.
* [getTimeSeriesTransitionMatrix](Analyzer-DataRetrievers-getTimeSeriesTransitionMatrix): This function generates the transfer function between discrete levels in a time series.
* [plotSetResult](Analyzer-DataRetrievers-plotSetResult): This plots one result from a set of simulations. 
* [readNCFile](Analyzer-DataRetrievers-readNCFile): Reads a net cdf file that has variables `time` and `value`, where value has the attributes `scale`, `offset` and `units` and time has the attribute `units`.
* [readXmlTag](Analyzer-DataRetrievers-readXmlTag): Returns a value from an xml tag.
