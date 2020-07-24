# Introduction
The `wtgDispatch` modules are used to dispatch the [wind turbines](WindTurbine-Class) (`wtg`) in a [wind farm](Windfarm-Class) (`wf`). If a`wtgDispatch` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `wtgDispatch` module is being used. The input variables will be put into the [projectWtgDispatchInputs](Model-Resources-Setup-projectWtgDispatchInputs) XML file corresponding to that particular `wtgDispatch`. For example, the input variables for [wtgDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/wtgDispatch0.py) will be stored in [projectWtgDispatch0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectWtgDispatch0Inputs.xml). Note that there are no inputs for `wtgDispatch0`. 

# Functions
## runDispatch
### Input variables
**wf**: a reference to the instance of the `wf` object whose `wtg` need to be dispatched. 

**newWtgP**: The desired new real power setpoint. 

**newWtgQ**: This is not implemented yet. It is the desired new reactive power setpoint. 

### Operation
`wtgDispatch` must take `newWtgP` and split it between the individual `wtg in the `wf`. The maximum power (`wtg.wtgPAvail`) should not be exceeded. The new powers should be assigned to the `wtg` (`wtg.wtgP`). 

# Modules
The `wtgDispatch` modules included in this software include: 
* [wtgDispatch0](Model-Controls-wtgDispatch0): load wind turbines based proportionally to their maximum rated power. 
