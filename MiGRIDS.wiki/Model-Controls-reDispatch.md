# Introduction
The `reDispatch` modules are used to dispatch any sources of renewable energy (at the moment only [wind power](Windfarm-Class)) and [thermal energy storage systems](ThermalEnergyStorageSystem-Class) (TESS). If an `reDispatch` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `reDispatch` module is being used. The input variables will be put into the [projectReDispatchInputs](Model-Resources-Setup-projectReDispatchInputs) XML file corresponding to that particular `reDispatch`. For example, the input variables for [reDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/reDispatch0.py) will be stored in [projectReDispatch0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectReDispatch0Inputs.xml).

# Functions
## reDispatch
### Input variables
**SO**: a reference to the instance of the [SystemsOperations](Model-Operational-SystemOperations) which runs the simulation logic.  

### Operation
`reDispatch` must determine how much wind power will be imported into the grid and how much will go into the TESS. The functions  `runWtgDispatch` and `runTesDispatch` need to be run from the [wind farm](Windfarm-Class) and the [TESS](ThermalEnergyStorageSystem-Class) with the power setpoints for the wind turbines import into the grid and input TESS imput, respectively. The amount available to charge the [electrical energy storage system](ElectricalEnergyStorageSystem-Class) needs to be saved in the local variable `wfPch`. 

# Modules
The `reDispatch` modules included in this software include: 
* [reDispatch0](Model-Controls-reDispatch0): implements a maximum rate of change in the power output of the wind turbines and uses the TESS to balance out fluctuations in the deviations between the power set point and actual output of the wind turbines. 
* [reDispatch1](Model-Controls-reDispatch1): No ramp rate limitations on the wind farm and no TESS implemented. 
