This describes a thermal energy storage (`tes`) class. Note that this is only a simple implementation. The internal temperature of the `tes` is not calculated or tracked. Thus there is no equivalent "state of charge". This would be a future feature. 

# Input Variables
**tesID**: The integer ID of the `tes`.

**tesT**: The initial temperature in Kelvin of the `tes`.

**tesState**: The initial operating state, 0 - off, 1 - starting, 2 - online.

**timeStep**: The length of the simulation steps in seconds. 

**tesDescriptor**: The [thermal energy storage descriptor XML files](tesDescriptor.xml-:-Thermal-Energy-Storage-System) for the `tes`. This should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/tes1Descriptor.xml`.

# Methods
**tesDescriptorParser(self, tesDescriptor)**: This opens and parses the [thermal energy storage descriptor XML files](tesDescriptor.xml-:-Thermal-Energy-Storage-System) and saves the information in local variables. 

**checkOperatingConditions(self)**: Checks if the `tes` is operating within defined bounds. If it is not it will set a flag. 
