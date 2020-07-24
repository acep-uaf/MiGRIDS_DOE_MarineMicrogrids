## `fixBadData`

### Description

This function replaces data that is considered erroneous based on comparison with the component parameters specified in the xml component Descriptor files. Values that are beyond the limits specified for a component are replaced using linear interpolation of the nearest surrounding values. Blocks of data that have repeated values are replaced with blocks of data from elsewhere in the dataset. If it is a multi-year dataset replacement data fill be drawn from the previous or following year. If it is a single year dataset, replacement data is drawn from surrounding data with matching day and time frame within 1 month of the missing data. Missing data that covers a time period of greater than 2 weeks creates a split in the dataframe such that a list of dataframes without gaps in data are created. 

### Inputs
**df**: [pandas.dataFrame] with the data read from the input files sorted in chronological order.

**setupDir**: [String] Path to set up directory with setup.xml.

**listOfComponents**: [List] A list of Components in the dataframe.

**runTimeSteps**: [pandas.TimeDelta] the unit to up or down sample the data into.

### Output
    DataClass object.