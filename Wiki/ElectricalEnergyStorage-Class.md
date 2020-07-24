This describes an electrical energy storage unit (`ees`). 

# Input Variables
**eesID**: The `ees` ID. Datatype: integer. 

**eesSOC**: The initial state of charge of the`ees`. Datatype: float. 

**eesStates**: The initial operating state, 0 - off, 1 - starting, 2 - online. Datatype: integer. 

**timeStep**: The length of the simulation steps in seconds. Datatype: integer or float. 

**eesDescriptor**: The [electrical energy storage descriptor XML file](eesDescriptor.xml-:-Electrical-Energy-Storage-System) for this `ees`. This should be a string with a path and file name  relative to the project folder, e.g., `/InputData/Components/ees1Descriptor.xml`.

**timeSeriesLength**: the number of steps in the simulation. Datatype: integer. 

# Methods
**eesDescriptorParser(self, eesDescriptor)**: This opens and parses the [electrical energy storage descriptor XML file](eesDescriptor.xml-:-Electrical-Energy-Storage-System) and saves the information in local variables. 

**checkOperatingConditions(self)**: Checks if the `ees` is operating within defined bounds. If it is not, it will trigger the respective cumulative energy counters. If the value of the counter goes above a defined limit, a flag is set which will initiate the generator scheduler in the [powerhouse](Powerhouse-Class). 

**findPchAvail(self, duration)**: This returns the available power the `ees` can accept for a given duration. 

**findPdisAvail(self,duration,kWReserved,kWsReserved)**: This returns the amount of discharge power that is available for a given duration (`duration`, seconds) given a certain discharge power (`kWReserved`, kW) and energy capacity (`kWsReserved`, kWs) are reserved and cannot be used.

**findLoss(self,P,duration)**: This returns the loss in kWs for a certain power (`P`, kW) and duration (`duration`, s) given the current state of charge and the `LossMap` of the `ees`. 

**setSRC(self, SRC)**: This sets the required SRC (sets the local variable `ees.eesSRC` to input `SRC`, in kW) the `ees` is required to supply and finds the minimum state of charge (updates the local variable `ees.eesMinSrcE`, in kWs)

**updatePScheduleMax(self)**: This updates local variable `ees.eesPScheduleMax` with the maximum power that the `ees` can be scheduled for when running the generator scheduler in [power house](Powerhouse-Class)



