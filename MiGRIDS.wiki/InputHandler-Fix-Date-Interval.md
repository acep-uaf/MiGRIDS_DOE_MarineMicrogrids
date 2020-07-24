## `fixDataInterval`

### Description

This function upsamples or downsamples the data to the desired measurement frequency. Values between sampling events will be replaced using linear interpolation. Large blocks of missing data generated through upsampling are filled with subsets of data from elsewhere in the dataset. 

### Inputs
**data**: A DataClass object with dataframe of clean data in which datetime is the row index and all other columns will be up or downsampled.

**interval**: A string specifying the desired sampling interval following pandas time interval specifications. Interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)

### Output
A DataClass object in which the cleaned dataframe is now either upsampled or downsampled based on the specified input time interval and original sampling interval.


## `isInline`

### Description

This function looks for missing data and repeated values indicating the sensor was not actually collecting data for the indicated timestamp. It calls checkDataGaps  to looks for gaps in the timestamp index that is greater than the median sampling interval and adds empty records where needed. The new records are filled with NA's and treated like inline data.

### Inputs
**s** [pandas.Series] the series to evaluate

### Outputs
[pandas.Series] series with gaps filled with NA