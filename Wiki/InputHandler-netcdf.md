## `dataframe2netcdf` 

### Description

This function converts the dataframe to a netCDF format, including meta data from the componentDescriptor files. 

### Inputs

**df**: Is the data frame to be converted to netCDF. The index must be a datetime index.

**components**: a list of Component objects

**saveLocation**: Where to save the netCDF files. If this is left empty, the user will be prompted to select a location. 

### Outputs
netcdf files.