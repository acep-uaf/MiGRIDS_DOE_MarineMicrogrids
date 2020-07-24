# Introduction
The `predictWind` modules are used to predict what the available wind power will be in the near future in order to determine which combination of diesel generators to bring online when scheduling the diesel generators. If a `predictWind` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `predictWind` module is being used. The input variables will be put into the [projectPredictWindInputs](Model-Resources-Setup-projectPredictWindInputs) XML file corresponding to that particular `predictWind`. For example, the input variables for [predictWind0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/predictWind0.py) will be stored in [projectPredictWind0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectPredictWind0Inputs.xml). In this case there are no inputs. 
# Functions
## predictWind
### Input variables
**SO**: a reference to the instance of the [SystemsOperations](Model-Operational-SystemOperations) which runs the simulation logic. 

### Operation
`predictLoad` must predict what the future wind will be and save it to the local variable `futureWind`. 

# Modules
The `predictWind` modules included in this software include: 
* [predictWind0](Model-Controls-predictWind0)
* [predictWind1](Model-Controls-predictWind1)
