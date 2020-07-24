**NOTE: in order to run optimization routines, a base case model run has to be available. That is a model run without energy storage in the mix.**

The Optimizer Package contains routines specific to the optimization algorithms for finding the ideal sized energy storage. The optimizer is setup such that there are flexible interfaces for optimization algorithms, calculation of system performance (here called 'fitness') and additional methods for narrowing the data scope to run simulations for optimizations on, and for narrowing the search space for energy storage power and energy capacities through initial data analysis. 

![MiGRIDS Optimizer Flow Diagram](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/GBSOptimizer%20Flow%20Diagram%20-%20Page%201.png)

The major class in Optimizer is the `optimize` in [optimize.py](optimize.py). In order to initiate an optimization an _optimize_ object has to be created. For full instructions on the methods see the [optimize.py Wiki page](optimize.py).

Additional sub-packages in the Optimizer package are Resources, FitnessFunctions, and OptimizationBoundaryCalculators. 

The **Resources** package contains the configuration file template ([optimizerConfig.xml](optimizerConfig.xml)) for optimize.py configuration. A configured copy of this file has to be available for any project that optimization is intended to be performed for and should be located in `<ProjectName>/InputData/Setup/`. 

The **FitnessFunctions** package contains the interface to calculate optimizer iteration fitness based on optimization objectives. The interface and current implementations are bundled in [getFitness.py](getFitness.py). 

The **OptimizationBoundaryCalculators** package contains an interface and implementations for determining initial estimates of the range of power and energy values that should be used during optimization. The interface is contained in [getOptimizationBoundaries.py](getOptimizationBoundaries.py). 
