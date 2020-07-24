This module contains the function `writeNCFile` which writes a time series to a netCDF file. 

# Inputs
**time_epoch**: a list or array of epoch time values, of same length as input `value`. 
**value**: A list or array of numeric values. 

**Scale**: A numeric value by which `value` needs to be scaled in order to get the true value.

**Offset**: A numeric value by which `value` needs to be offset by in order to get the true value. 

**Units**: A string indicating what the units of `value` are, after scale and offset have been applied. 

**SaveName**: The name to save under which the file is saved. 