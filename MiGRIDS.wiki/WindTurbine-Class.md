This describes one wind turbine. 

# Input Variables
**wtgID**: The wind turbine ID, which should be an integer.

**windSpeedDir**: The directory where the windspeed file is saved. 

**wtgState**: The initial wind turbine operating state, 0 - off, 1 - starting, 2 - online.

**timeStep**: The length of the simulation time steps in seconds. 

**wtgDescriptor**: The [wind turbine descriptor XML file](wtgDescriptor.xml-:-Wind-Turbine-Generator). This should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/wtg1Descriptor.xml`.  

**timeSeriesLength**: the number of steps in the simulation. 

**runTimeSteps**: The timesteps to run. This can be 'all', an integer that the simulation runs up till, a list
        of two values of the start and stop indices, or a list of indices of length greater than 2 to use directly. Defualt is 'all'. 

# Methods
**wtgDescriptorParser(self, windSpeedDir, wtgDescriptor)**: This opens and parses the [wind turbine descriptor XML file](wtgDescriptor.xml-:-Wind-Turbine-Generator) and saves the information in local variables. It also calls `getWP` in order to convert the time series of wind speeds to wind power and save to a local variable. 

**getWP(self,PCpower,PCws,windSpeed, wsScale)**: Converts a a time series of wind speeds and a power curve into a time series of wind power. It uses interger list indexing because of its speed. `PCws` is an integer list of wind speeds scaled by 1/`wsScale` m/s. In other words, values in `windSpeed` are multiplied by `wsScale` in order to get values in m/s. `PCpower` is the corresponding integer list of wind turbine power, in kW. `windSpeed` is a list of windspeeds in m/s.

**checkOperatingConditions(self)**: Updates the run time of the wind turbine and the spilled wind power. A counter keeps track of the kWh of spilled wind power within a defined amount of time. If it goes above a certain threshold, a flag is set which will initiate the generator scheduler in the [powerhouse](Powerhouse-Class). 

**getWtgPAvail(self)**: Updates the value of the local variable `wtgPAvail`, which is the maximum output power available from this wind turbine. If it is online, it is equal to the current step value of its wind power time series. Otherwise it is zero. 

