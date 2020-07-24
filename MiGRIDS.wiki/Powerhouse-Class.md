The Powerhouse class contains a group of [diesel generators](Generator-Class) that operate together to supply a firm power source into the grid. They are dispatched each time step to supply the difference required between the different generating sources and the load. The generator scheduler is called to when there is either too much or too little generation capacity online compared to the load. The scheduler switches generators on and off-line. 

Note that a future feature for this class is to make the generator dispatch and scheduler separate modules that allow different dispatch and schedule schemes. 

# Input Variables
**genIDS**: A list of generator IDs representing each [diesel generator](Generator-Class) in the powerhouse. The IDs should be intergers. 

**genStates**: A list of the operating states of each generator at the start of the simulation, where `0` represents offline, `1` represents starting up and `2` represents running. Not having adequate capacity running at the start could cause an overloading situation on the generators.

**timeStep**: the time step the simlation is being run at, in seconds. 

**genDescriptor**: A list of [generator descriptor XML files](genDescriptor.xml-:-Diesel-Electric-Generator) for the respective generators listed in `genIDS`, this should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/gen1Descriptor.xml`. 

**genDispatchFile**:The path to the class that dispatches the generators energy in the powerhouse. Options included in the software package are listed [here](genDispatch).  A user can also write their own class which needs to follow the rules listed in the previous link. 

**genScheduleFile**: The path to the class that schedules the generators energy in the powerhouse. Options included in the software package are listed [here](genSchedule).  A user can also write their own class which needs to follow the rules listed in the previous link. 

**genDispatchInputsFile**: The path to the [xml file](projectGenDispatchInputs) that provides the inputs to the genDispatch. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameGenDispatch0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `genDispatch` class, then they will need to create their own `projectGenDispatchInput` xml file as well.

**genScheduleInputsFile**: The path to the [xml file](projectGenScheduleInputs) that provides the inputs to the genSchedule. A copy of this file is saved in the `projectName/Setup/UserInput/` folder. The file name will change to `projectNameGenSchedule0.py`, for example, where `projectName` is the name of the project.  If the user writes their own `genSchedule` class, then they will need to create their own `projectGenScheduleInput` xml file as well.

# Methods
**combFuelCurves(self, genIDs)**: This combines the fuel curves for different combinations of generators. In other words, this is the effective fuel curve for when a particular group of generators are running online. `genIDs` are the IDs of the generators whose fuel curves are being combined. 

**combMaxDiesCapCharge(self, genIDs)**: This combines the `maximum diesel capacity charging` for different combinations of diesel generators. This sets the limit on how high the loading on the diesel generators can go in order to charge the energy storage system. See the [generator descriptor XML files](genDescriptor.xml-:-Diesel-Electric-Generator) for a more thorough description. 

**runGenDispatch(self, newGenP, newGenQ)**: This runs the [generator dispatch](genDispatch.py) and then checks the operating conditions of each generator. 

**runGenSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay,underSRC)**: This runs the [generator schedule](genSchedule). 

**switchGenComb(self,GenSwOn, GenSwOff)**: Switches generators on and offline. `GenSwOn` and `GenSwOff` are the IDs of the generators to switch on and offline. 

**startGenComb(self, GenSwOn)**: This starts warming up diesel generators so that they can be brought online. 

**isfloat(self,x)**: Checks if `x` can be converted to float. 

**isint(self,x)**: Checks if `x` can be converted to int. 

**isbool(self,x)**: Checks if `x` can be converted to bool. 

**returnObjectValue(self, obj)**: returns the value of an object, either as an int, float, bool or string, depending on what it can be converted to. 
