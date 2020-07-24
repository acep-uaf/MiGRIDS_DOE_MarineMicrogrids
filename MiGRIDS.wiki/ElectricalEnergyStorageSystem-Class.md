This describes a system of one or more [electrical energy storage units](ElectricalEnergyStorage-Class). 

# Input Variables
**eesIDS**: A list of integers for identification of electrical energy storage units.

**eesSOCs**: A list of initial states of charge of the electrical energy storage units.

**eesStates**: A list of the initial operating state, 0 - off, 1 - starting, 2 - online.

**timeStep**: The length of the simulation steps in seconds. 

**eesDescriptors**: A list of [electrical energy storage descriptor XML files](eesDescriptor.xml-:-Electrical-Energy-Storage-System) for the respective electrical energy storage units listed in `eesIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/ees1Descriptor.xml`.

**eesDispatchFile**: The path to the class that dispatches the electrical energy storage units in the grid. Options included in the software package are listed in [eesDispatch](eesDispatch). A user can also write their own class. It needs to follow the instructions listed in [eesDispatch](eesDispatch).

**eesDispatchInputsFile**: The path to the [xml file](eesDispatchInputs) that provides the inputs to the eesDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameEesDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `eesDispatch` class, then they will need to create their own `projectEesDispatchInput` xml file as well.

**timeSeriesLength**: the number of steps in the simulation. 

# Methods
**runEesDispatch(self, newP, newQ, newSRC, tIndex)**: This runs the [electrical energy storage Dispatch](eesDispatch) and then checks the operating conditions of each electrical energy storage unit. 

**updateEesPScheduleMax(self)**: This updates maximum power that each electrical energy storage unit is able to provide (for one time step). 


