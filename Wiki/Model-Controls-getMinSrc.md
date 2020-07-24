# Introduction
The `getMinSrc` modules are used to determine how much spinning reserve capacity (SRC) is required in the grid at each simulation step. If a `getMinSrc` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `getMinSrc` module is being used. The input variables will be put into the [projectGetMinSrcInputs](Model-Resources-Setup-projectGetMinSrcInputs) XML file corresponding to that particular `getMinSrc`. For example, the input variables for [getMinSrc0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/getMinSrc0.py) will be stored in [projectGetMinSrc0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectGetMinSrc0Inputs.xml). In this case there is one input. 
# Functions
## getMinSrc
### Input variables
**SO**: a reference to the instance of the [SystemsOperations](Model-Operational-SystemOperations) which runs the simulation logic. 

**calcFuture**: A bool value that indicates whether the `SRC` value desired is the current value (`calcFuture` = False) or a predicted future value (`calcFuture` = True).  

### Operation
`getMinSrc` must calculate the required `SRC` based on the required percentage of the [load](Demand-Class) and the [wind turbines](WindTurbine-Class). When other variable energy sources are implemented, such as solar-PV, then those will need to be taken into account as well. Two local variable must be updated: `minSrcToStay` and `minSrcToSwitch`. These are the minimum SRC required if keeping the current combination of diesel generators online and if switching the online combination of diesel generators, respectively. Assigning a higher SRC requirement to switch to a different generator combination can be used to reduce diesel switching.  

# Modules
The `getMinSrc` modules included in this software include: 
* [getMinSrc0](Model-Controls-getMinSrc0)
