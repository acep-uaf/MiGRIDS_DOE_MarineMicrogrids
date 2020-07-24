# Introduction
The `predictLoad` modules are used to predict what the load will be in the near future in order to determine which combination of diesel generators to bring online when scheduling the diesel generators. If a `predictLoad` module is created, then it needs to follow the description below. 

# Input Variables
Input variables depend on which `predictLoad` module is being used. The input variables will be put into the [projectPredictLoadInputs](Model-Resources-Setup-projectPredictLoadInputs) XML file corresponding to that particular `predictLoad`. For example, the input variables for [predictLoad0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/predictLoad0.py) will be stored in [projectGetMinSrc0Inputs](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Resources/Setup/projectPredictLoad0Inputs.xml). In this case there are no inputs. 
# Functions
## predictLoad
### Input variables
**SO**: a reference to the instance of the [SystemsOperations](Model-Operational-SystemOperations) which runs the simulation logic. 

### Operation
`predictLoad` must predict what the future load will be and save it to the local variable `futureLoad`. 

# Modules
The `predictLoad` modules included in this software include: 
* [predictLoad0](Model-Controls-predictLoad0)
