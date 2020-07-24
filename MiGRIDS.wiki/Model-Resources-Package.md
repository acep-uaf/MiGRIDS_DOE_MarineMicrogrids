This package is a subset of the [**Model Package**](Model-Package) and contains resources to setup the model. 

There are the following subpackages:
* [Components](Model-Resource-Components-Package), which contains descriptor interfaces and implementations for power system components
* [Setup](Model-Resources-Setup), which contains the interfaces containing input information for components and simulation modules. 

# Implementation
Multiple XML files are used to determine which components and control modules are run in the simulations as well as their input configuration values. The following diagram shows how these files relate to each other.  When setting up a project,[project setup](projectSetup-XML) and [Control module input](Model-Resources-Setup-projectControlModuleInputs) xml files are placed in the `projectName/InputData/Setup` directory and [Component descriptor](Model-Resource-Components-Package) xml files are placed in the `projectName/InputData/Components` directory. These represent the base case that can be modified in each set of simulations.  

When creating a set of simulations to run, a [set attributes](projectSetAttributes-XML) xml file is placed in `projectName/OutputData/Setx` where `x` is the set identifier, for example `Set0`. This file contains any changes to the default values in the xml files saved in the `projectName/InputData` directory. When [generateRuns.py](generateRuns) is run, it will copy and make changes to the input xml files and place them in `projectName/OutputData/Setx/Setup` and `projectName/OutputData/Setx/Runy/Components`, where `y` is the simulation run number. A set of simulations will contain as many runs as there are unique combination of changes to the default [component descriptor files](Model-Resource-Components-Package). 

After generating simulation runs, [runSimulation.py](runSimulation) is run to run the simulations. See the [Project flow and directory structure](Project-flow-and-directory-structure) and [tutorials](Project-tutorials) pages for more information on setting up and running simulations in a project. 

![A diagram showing the relationship between setup xml files.](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/Setup%20xml%20files%201.png)
