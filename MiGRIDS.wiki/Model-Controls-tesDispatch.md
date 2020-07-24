# Introduction
The `tesDispatch` modules are used to dispatch the [thermal energy storage units](ThermalEnergyStorage-Class) (TES) in a [thermal energy storage system](ThermalEnergyStorageSystem-Class) (TESS). If a`tesDispatch` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `tesDispatch` module is being used. The input variables will be put into the [projectTesDispatchInputs](Model-Resources-Setup-projectTesDispatchInputs) XML file corresponding to that particular `tesDispatch`. For example, the input variables for [tesDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/tesDispatch0.py) will be stored in [projectTesDispatch0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectTesDispatch0Inputs.xml). Note that there are no inputs for `tesDispatch0`. 

# Functions
## runDispatch
### Input variables
**TESS**: a reference to the instance of the [TESS](ThermalEnergyStorageSystem-Class) object whose [TES](ThermalEnergyStorage-Class) need to be dispatched. 

**P**: The desired new real power setpoint. 

### Operation
`tesDispatch` must take `P` and split it between the individual [TES](ThermalEnergyStorage-Class) in the [TESS](ThermalEnergyStorageSystem-Class). The maximum power (`tes.tesPAvail`) should not be exceeded. The new powers should be assigned to the `TES` (`tes.tesP`). 

# Modules
The `tesDispatch` modules included in this software include: 
* [tesDispatch0](Model-Controls-tesDispatch0): charge proportional to their maximum power capabilities. 
