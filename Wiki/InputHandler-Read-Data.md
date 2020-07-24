
## `readAllTimeSeries`

### Description

Cycles through a list of files in CSV format and imports them into a single dataframe.


### Inputs

**inputDict**: [Dictionary] with attribute of fileName and attributes needed in readAvecCSV (see below).
### Outputs
pandas.DataFrame with data from all input files.

## `readDataFile`
### Description

Calls the appropriate read method (CSV or MET) and compiles these data into a standardized data frame.

### Inputs

**inputSpecification**: [String] indicating the input format of the data. Currently the only recognized input is 'AVEC'. 

**fileLocation**: [String] The directory where the data files are stored. It is either absolute or relative to the MiGRIDS project InputData directory. Default is the InputData directory. 

**fileType**: [String]The file type of input data files. All files of this type will be read from the fileLocation directory. Default is 'csv'. 

**columnNames**: [List of String] Is a list of column names (taken from the header in the input data files) that will be read and returned in the output. It can be a list of names of column indices. Note that indexing starts from 0. If not defined, all columns will be returned. 

**useNames**: [List of String] Is a list of the same size as `columnNames`. It has a list of the variable names to be used instead of the names in the header from the files. These names must correspond to implementations of the componentDescriptor files. 


**componentUnits**: [List of String] Is a list of the units corresponding to the `columnNames` for the input data. It is used to convert the data to the standard units used internally in the model. 

**componentAttributes**: [List of String] Is the attribute being measured, for example, `P` (power) 'WS` (wind speed) etc. The naming convention is listed in the 'netCDF Naming Conventions.pdf' file located in `MiGRIDS\Resources\Conventions`


### Output

[pandas.DataFrame] with the data read from the input files. 

[list of Components] including names, units, attribute, scale and offset.

## `readWindData`

### Description

Imports all MET data files in a folder and converts parameters to a dataframe. Assumes MET files consist of header information and data records. A Langevin estimator us used to fill in timesteps between records.
### Inputs
**inputDict**: [Dictionary] a dictionary containing file location, datetime and channel information.
### Outputs
[Dictionary] a dictionary of files that were read.
[pandas.DataFrame] the resulting dataframe of values is returned.
