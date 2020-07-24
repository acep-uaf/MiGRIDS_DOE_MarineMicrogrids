The module `getRunMetaData` contains the functions `getRunMetaData` and `loadResults`. `getRunMetaData` saves select meta data for a set of simulations into an SQL data base and a CSV file, as `SetxResults.db` and `SetxResults.csv`, respectively. `getRunMetaData` calls `loadData` to get data from one netCDF file. This [test script](TestScripts-getRunMetaDataSandbox) contains a sample implementation. 

## projectSetDir Inputs
**projectSetDir**: the directory of the project set, such as `projectName/OutputData/Setx` where `x` is the set identifier. 

**runs**: The simulation runs to analyze. This is a list of integers corresponding to the set numbers. 

## loadResults Input and Output
**fileName**: The filename of the netCDF file to load results from.

**location**: The directory of the netCDF file. This can be left empty. 

**returnTimeSeries**: Is a bool value that indicates whether to return the time series of time stamps. If False, then the timeStep is returned. Otherwise the time stamp time series is returned. Default is False. 

**returns**: `[valMean, valSTD, valMax, valMin, valInt], val, time/timeStep`

where  `valMean, valSTD, valMax, valMin, valInt` are the mean, standard deviation, maximum, minimum and the integral over seconds of the netCDF `value` variable. `val` is the netCDF `value` variable with attributes `Scale` and `Offset` applied. `time` is the series of time stamps and `timeStep` is the mean time step of the time stamps. `returnTimeSeries` determines whether `time` or `timeStep` is returned. 
