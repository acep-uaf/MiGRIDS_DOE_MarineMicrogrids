The Windfarm class contains WindTurbine objects that it dispatches based on power set points. 

# Inputs
**wtgIDS**: A list of wind turbine IDs, which should be integers.

**wtgSpeedDir**: The directory (or list of directories the same length as `wtgIDS`) where the netCDF file containing the time series of wind speeds is located. 

**wtgStates**: A list of the initial wind turbine operating states 0 - off, 1 - starting, 2 - online.

**timeStep**: The timestep the simulation is run at, in seconds. 

**wtgDescriptors**: A list of [wind turbine descriptor XML files](wtgDescriptor.xml-:-Wind-Turbine-Generator) for the respective wind turbines listed in `wtgIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/wtg1Descriptor.xml`. 

**timeSeriesLength**: the number of steps in the simulation. 

**wtgDispatchFile**: The path to the class that dispatches the wind turbines in the wind farm. Options included in the software package are listed [here](wtgDispatch).  A user can also write their own class which needs to follow the rules listed in the previous link.

**wtgDispatchInputsFile**: The path to the [xml file](wtgDispatchInputs) that provides the inputs to the wtgDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameWtgDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `wtgDispatch` class, then they will need to create their own `projectWtgDispatchInput` xml file as well.

**runTimeSteps**: The timesteps to run. This can be 'all', an integer that the simulation runs up till, a list
        of two values of the start and stop indices, or a list of indices of length greater than 2 to use directly. Defualt is 'all'. 

# Methods
**runWtgDispatch(self, newWtgP, newWtgQ, tIndex)**: This runs the [wind turbine dispatch](wtgDispatch) and then checks the operating conditions of each wind turbine.

**getWtgPAvail(self, idx)**: This updates the power available from each wind turbine based on the simulation time step. 
