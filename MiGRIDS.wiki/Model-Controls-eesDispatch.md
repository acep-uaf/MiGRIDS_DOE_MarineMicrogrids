# Introduction
The `eesDispatch` modules are used to dispatch the electrical energy storage units (EES) in an electrical energy storage system (EESS). If an `eesDispatch` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `eesDispatch` module is being used. The input variables will be put into the [projectEesDispatchInputs](Model-Resources-Setup-projectEesDispatchInputs) XML file corresponding to that particular `eesDispatch`. For example, the input variables for [eesDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/eesDispatch0.py) will be stored in [projectEesDispatch0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectEesDispatch0Inputs.xml). Note that there are no inputs for `eesDispatch0`. 

# Functions
## runDispatch
### Input variables
**eess**: a reference to the instance of the [EESS](ElectricalEnergyStorageSystem-Class) object whose [EES](ElectricalEnergyStorage-Class) need to be dispatched. 

**newP**: The desired new real power setpoint. 

**newQ**: This is not implemented yet. It is the desired new reactive power setpoint. 

**newSRC**: The desired spinning reserve capacity (SRC) to be provided by the EESS. 

**tIndex**: The index of the current simulation step. 

### Operation
`eesDispatch` must take `newP` and split it between the individual [EES](ElectricalEnergyStorage-Class) in the [EESS](ElectricalEnergyStorageSystem-Class). The maximum charging and discharging (`ees.eesPinAvail` and `ees.eesPoutAvail`) should not be exceeded. The new powers should be assigned to the `EES` (`ees.eesP`). The `EES` function `checkOperatingConditions` should be called for each `EES` after being assigned their new power. The `EES` function `setSRC` should be used to assign how much SRC each `EES` will supply. Unlike for power, even if the `EES` are not able to supply all the requested `newSRC`, they should still be assigned the full `newSRC` amount. This will be tracked as under-SRC operation in the `EESS` where a counter keeps track of how much under-SRC operation there has been and will set a flag if it passes a threshold. 

# Modules
The `eesDispatch` modules included in this software include: 
* [eesDispatch0](Model-Controls-eesDispatch0): proportional charging and discharging
* [eesDispatch1](Model-Controls-eesDispatch1): prioritized charging and discharging
