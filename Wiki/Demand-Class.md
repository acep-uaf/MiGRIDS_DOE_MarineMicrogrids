This describes a load time series. This is used to represent electrical loads in the grid. 

# Input Variables
**timeStep**: The length of time steps the simulation is run at in seconds.

**loadRealFiles**: NetCDF files of the real load. They need to have the variables `time` and `value`. `time` needs to be in epoch time. `value` needs to have units of kW. This can be one file or a list of files that add up to the total load. 

**loadDescriptor**: The [load descriptor XML file](loadDescriptor.xml-:-Generic-Load). This should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/load1Descriptor.xml`. 

**loadReactiveFiles**: This is not implemented yet, it is a future feature. 

**runTimeSteps**: This indicates which simulation steps to run. If "all" of ":", then all steps will be run. If a single integer, then it will run up to that index. If two integers, then it will run from the first to the second integer. If it a list of length greater than 2, then they will be read as the actual indices to run. The default value is "all". 

# Methods
**loadDescriptorParser(self, loadDescriptor)**: This opens and parses the [load descriptor XML file](loadDescriptor.xml-:-Generic-Load) and saves the information in local variables. 

**loadLoadFiles(self, loadFiles)**: Reads in the load files, if there are more than one, sum them, and returns the result. 

**checkNCFile(self, ncFile, isReal=True)**: This checks if there are any NAN values in the file, which will throw an error. If the units for the netCDF variable `time` are not `s`, `sec` or `seconds` (case insensitive) then it will throw an error. If `isReal` is True or False and the units for variable `value` are not `kW` or `kvar` (case insensitive) respectively, then it will throw an error. Otherwise, it will return the time and value arrays, with value scaled by netCDF variable `value`'s attributes `scale` and offset by `offset`. 
 
