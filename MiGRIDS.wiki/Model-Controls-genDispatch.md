# Introduction
The `gesDispatch` modules are used to dispatch the [diesel generators](Generator-Class) (`gen`) in a [powerhouse](Powerhouse-Class) (`ph`). If a `genDispatch` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `genDispatch` module is being used. The input variables will be put into the [projectGenDispatchInputs](Model-Resources-Setup-projectGenDispatchInputs) XML file corresponding to that particular `genDispatch`. For example, the input variables for [genDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/genDispatch0.py) will be stored in [projectGenDispatch0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectGenDispatch0Inputs.xml). Note that there are no inputs for `genDispatch0`. 

# Functions
## runDispatch
### Input variables
**ph**: a reference to the instance of the [powerhouse](Powerhouse-Class) object whose [diesel generator](Generator-Class) need to be dispatched. 

**newGenP**: The desired new real power setpoint. 

**newGenQ**: This is not implemented yet. It is the desired new reactive power setpoint. 

### Operation
`genDispatch` must take `newGenP` and split it between the individual `gen` in the `ph`. The maximum power available (`gen.genPAvail`) should not be exceeded. The new powers should be assigned to the `gen` (`gen.genP`). Even if the `gen` are not able to supply all the requested power `newGenP`, it should still be assigned. This will be tracked as overloading operation in the `ph`. Post processing of the data will determine if this was a blackout or brownout. 

# Modules
The `genDispatch` modules included in this software include: 
* [genDispatch0](Model-Controls-genDispatch0): proportional dispatch
