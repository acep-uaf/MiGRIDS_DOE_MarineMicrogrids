This thermal energy storage system (`tess`) class describes a system of one or more [thermal energy storage units]ThermalEnergyStorage-Class) (`tes`). 

# Input Variables
**tesIDS**: A list of integers for identification of the `tes` that make up this `tess`.

**tesT**: A list of initial temperatures in Kelvin of the `tes` units.

**tesStates**: An integer list of the initial operating states, 0 - off, 1 - starting, 2 - online.

**timeStep**: The length of the simulation steps in seconds. 

**tesDescriptors**: A list of [thermal energy storage descriptor XML files](tesDescriptor.xml-:-Thermal-Energy-Storage-System) for the respective `tes` units listed in `tesIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/tes1Descriptor.xml`.

**tesDispatchFile**: The path to the class that dispatches the thermal energy storage units in the grid. Options included in the software package are listed in [tesDispatch](Model-Controls-tesDispatch). A user can also write their own class. It needs to follow the instructions listed in [tesDispatch](Model-Controls-tesDispatch).

**tesDispatchInputsFile**: The path to the [xml file](Model-Resources-Setup-projectTesDispatchInputs) that provides the inputs to the `tesDispatch`. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. If `tesDispatch0` is used, the file name will change to `projectNameTesDispatch0Inputs.py`, for example, where `projectName` is the name of the project.  If the user writes their own `tesDispatch` class, then they will need to create their own `projectTesDispatchInput` xml file as well.

# Methods
**runTesDispatch(self, newP)**: This runs the [thermal energy storage Dispatch](Model-Controls-tesDispatch) and then checks the operating conditions of each `tes` unit. 

**checkOperatingConditions(self)**: This checks if the `tes` is operating outside of its rated bounds. 


