This describes a diesel generator. 

# Input Variables
**genID**: The integer ID of this generator

**genState**: The initial generating state of this generator at the beginning of the simulation, where `0` represents offline, `1` represents starting up and `2` represents running. 

**timeStep**: The length of time steps the simulation is run at in seconds.

**genDescriptor**: The [generator descriptor XML file](genDescriptor.xml-:-Diesel-Electric-Generator). This should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/gen1Descriptor.xml`. 

# Methods
**genDescriptorParser(self, genDescriptor)**: This opens and parses the [generator descriptor XML file](genDescriptor.xml-:-Diesel-Electric-Generator) and saves the information in local variables. 

**checkOperatingConditions(self)**: Checks if the generator is operating within defined bounds. If it is not, it will trigger the respective cumulative energy counters. If the value of the counter goes above a defined limit, a flag is set which will initiate the generator scheduler in the [powerhouse](Powerhouse-Class). 

**updateGenPAvail(self)**: Updates the value of the local variable `genPAvail`, which is the maximum output power available from this generator. If it is online, it is equal to generator's rated power, otherwise it is zero. 
