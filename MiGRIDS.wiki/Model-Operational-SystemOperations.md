The `SystemsOperations` class is used to load the required files and run one simulation.  The output data from the simulation is stored in the internal `SystemOperations` object. 

# Input Variables
**timeStep:** the length of time steps the simulation is run at in seconds.

**runTimeSteps**: the timesteps to run. This can be 'all', an integer that the simulation runs up till, a list
        of two values of the start and stop indices, or a list of indices of length greater than 2 to use directly.

**loadRealFiles**: list of the paths to netCDF files that add up to the full real load

**loadReactiveFiles**: list of the paths to netCDF files that add up to the full reactive load. This can be left empty. The simulation is not currently set up to run reactive loads. 

**predictLoad**: This is a class that is called when the online generating combination is being changed. It predicts what the load will be in the near future for the purpose of deciding what size of generating units to bring online. If a user defines their own load predicting class, it is the path and filename of the class used to predict short term (several hours) future load. Otherwise, it is the name of the dispatch filename included in the software package. Options include: [predictLoad0](predictLoad0.py). If a user creates their own function, it must follow the input and outputs described in [predictLoad0](predictLoad0.py). 

**loadDesciptor**: The [xml descriptor file](loadDescriptor.xml-:-Generic-Load) that describes the load to be used in the simulation. 

**predictWind**: This is a class that is called when the online generating combination is being changed. It predicts what the available wind power will be in the near future for the purpose of deciding what size of generating units to bring online. If a user defines their own wind predicting class, it is the path and filename of the class used to predict short term (several hours) future available wind power. Otherwise, it is the name of the dispatch filename included in the software package. Options include: [predictWind0](predictWind0.py) and [predictWind1](predictWind1.py). If a user creates their own function, it must follow the input and outputs described in either of those classes. 

**getMinSrcFile**: The path to the class that determines the minimum amount of spinning reserve capacity (SRC) required at each timestep in the simulation. Options included in the software package include: [getMinSrc0](getMinSrc0.py). A user can also write their own class. It needs to follow the instructions listed in [getMinSrc0](getMinSrc0.py). 

**reDispatchFile**: The path to the class that dispatches the renewable energy in the grid. Options included in the software package include: [reDispatch0](reDispatch0.py) and [reDispatch1](reDispatch1.py). A user can also write their own class. It needs to follow the instructions listed in either [reDispatch0](reDispatch0.py) or [reDispatch1](reDispatch1.py). 

**reDispatchInputsFile**: The path to the xml file that provides the inputs to the reDispatch. For the two dispatches provided in this software ([reDispatch0](reDispatch0.py) and [reDispatch1](reDispatch1.py)) the files [projectReDispatch0Inputs.xml](projectReDispatch0Inputs.xml) and [projectReDispatch1Inputs.xml](projectReDispatch1Inputs.xml) are provided in `MiGRIDS/Model/Resources/Setup`. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameReDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `reDispatch` class, then they will need to create their own `projectReDispatchInput.xml` file as well. 

**genIDS**: list of generator IDs, which should be integers

**genStates**: A list of the operating states of each generator at the start of the simulation, where `0` represents offline, `1` represents starting up and `2` represents running. Not having adequate capacity running at the start could cause an overloading situation on the generators. 

**genDescriptors**: A list of [generator descriptor XML files](genDescriptor.xml-:-Diesel-Electric-Generator) for the respective generators listed in `genIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/gen1Descriptor.xml`. 

**genDispatchFile**:The path to the class that dispatches the generators energy in the powerhouse. Options included in the software package are listed [here](genDispatch).  A user can also write their own class which needs to follow the rules listed in the previous link. 

**genScheduleFile**: The path to the class that schedules the generators energy in the powerhouse. Options included in the software package are listed [here](genSchedule).  A user can also write their own class which needs to follow the rules listed in the previous link. 

**genDispatchInputsFile**: The path to the [xml file](projectGenDispatchInputs) that provides the inputs to the genDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameGenDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `genDispatch` class, then they will need to create their own `projectGenDispatchInput` xml file as well.

**genScheduleInputsFile**: The path to the [xml file](projectGenScheduleInputs) that provides the inputs to the genSchedule. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameGenSchedule0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `genSchedule` class, then they will need to create their own `projectGenScheduleInput` xml file as well.

**wtgIDS**: A list of wind turbine IDs, which should be integers.

**wtgStates**: A list of the initial wind turbine operating states 0 - off, 1 - starting, 2 - online.

**wtgDescriptors**: A list of [wind turbine descriptor XML files](wtgDescriptor.xml-:-Wind-Turbine-Generator) for the respective wind turbines listed in `wtgIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/wtg1Descriptor.xml`. 

**wtgSpeedFiles**: A list of the netCDF files containing the wind speeds at each time step in the simulation. The length of these files must correspond with the length of the load time series file that is in input to the [Demand](Demand-Class) class. 

**wtgDispatchFile**: The path to the class that dispatches the wind turbines in the wind farm. Options included in the software package are listed [here](wtgDispatch).  A user can also write their own class which needs to follow the rules listed in the previous link.

**wtgDispatchInputsFile**: The path to the [xml file](wtgDispatchInputs) that provides the inputs to the wtgDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameWtgDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `wtgDispatch` class, then they will need to create their own `projectWtgDispatchInput` xml file as well.

**eesIDS**: A list of integers for identification of electrical energy storage units.

**eesStates**: A list of the initial operating state, 0 - off, 1 - starting, 2 - online.

**eesSOCs**: A list of initial states of charge of the electrical energy storage units.

**eesDescriptors**: A list of [electrical energy storage descriptor XML files](eesDescriptor.xml-:-Electrical-Energy-Storage-System) for the respective electrical energy storage units listed in `eesIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/ees1Descriptor.xml`.

**eesDispatchFile**: The path to the class that dispatches the electrical energy storage units in the grid. Options included in the software package include: [eesDispatch](eesDispatch). A user can also write their own class. It needs to follow the instructions listed in [eesDispatch](eesDispatch).

**eesDispatchInputsFile**: The path to the [xml file](eesDispatchInputs) that provides the inputs to the eesDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameEesDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `eesDispatch` class, then they will need to create their own `projectEesDispatchInput` xml file as well.

**tesIDS**: A list of integers for identification of thermal energy storage units.

**tesStates**: A list of the initial operating state, 0 - off, 1 - starting, 2 - online.

**tesTs**: A list of initial temperatures of the thermal energy storage units.

**tesDescriptors**: A list of [thermal energy storage descriptor XML files](tesDescriptor) for the respective thermal energy storage units listed in `tesIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/tes1Descriptor.xml`.

**tesDispatchFile**: The path to the class that dispatches the thermal energy storage units in the grid. Options included in the software package include: [tesDispatch](tesDispatch). A user can also write their own class. It needs to follow the instructions listed in the previous link. 

**tesDispatchInputsFile**: The path to the [xml file](tesDispatchInputs) that provides the inputs to the tesDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameTesDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `tesDispatch` class, then they will need to create their own `projectTesDispatchInput` xml file as well.

# Methods
**runSimulation(self)**: This is the only method that needs to be called by the user. This will run the simulations and save the output files in the project directory. There are no inputs. 

**dumpVariable(self,var,varName,snippetIdx)**: This dumps the specified variable into a pickle. This is used when a simulation is broken up and run in segments in order to reduce the memory required. `var` is the variable, `varName` is the name used in the pickle file name and `snippetIdx` identifies which simulation segment this variable was saved for. 

**dumpAllVariables(self,snippetIdx,resultLenght)**: This dumps all simulation variables from a specific simulation segment into pickles. `snippetIdx` identifies which segment the variables come from and `resultLength` is used to initiate new data channels for the variables in the next simulation segment. 

**stitchVariable(self, varName)**: This stitches together the pickled variable time series from the different simulation segments into one time series.

**initDataChannels(self, varLength)**: This Initializes all data channels that are being tracked with a given length (`varLength`). This function is called by runSimulation() and by dumpAllTSVars().

**runSimMainLoop(self)**: This is the main loop that is iterated through to run a simulation. It is called by `runSimulation`. 



