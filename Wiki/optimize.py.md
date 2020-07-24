optimize.py contains a single class called `optimize` which is used to generate an optimization object. The main methods of this class are described below. 

Typically, the following lines of code are used to initiate, and execute the optimization, and retrieve results for further study. 

```
from Optimizer.optimize import optimize

# Create optimize object and initialize. 
myOptimizationObject = optimize(<myOptimizationProjectName>, []) # empty second argument is place holder for later addition of other args

# Execute optimization
myOptimizationObject.doOptimization() 

# Retrieve log of results. This can be analyzed to determine which iteration yielded the best result, and what the power and energy values for the EES were. 
fitnessLog = myOptimizationLog.fl
```

# Initialization
`__init__` is the constructor for the optimizer object and contains vital configuration and initial configurations tasks. An optimization object is created by calling `myOptimizationObject = optimize('myProjectName', inputArgs)`, where `myProjectName` has to be identical to the project folder name in the `MiGRIDSProjects` folder, and `inputArgs` is a spare input argument to pass additional information as needed. It currently is unused, other than that it's contents is written to the global variable `self.inputArgs` which can be passed on and then unravelled in interfacing methods. 

The `__init__` method sets up key project parameters by reading `optimizerConfig<myProjectName>.xml`, which is required to be located in the `../../MiGRIDSProjects/<myProjectName>/InputData/Setup/` folder and needs to contain all tag described in [`optimizerConfig.xml`](../wiki/optimizerConfig.xml). Based on this configuration, the base case is loaded. That is, a simulation run without energy storage online. **This case is required to be available in `<myProjectName>/InputData/TimeSeriesData/ProcessedData/`**. 

From the base case, and based on the configuration of `self.boundaryMethod` optimization boundaries (min and max power and energy values for the energy storage system to consider) are determined by calling the interface in [`getOptimizationBoundaries.py`](../wiki/getOptimizationBoundaries.py). 

Next, shorter time-series are calculated based on the configuration in `self.dataReductionMethod` by calling the `getDataSubsets` interface. The objective of this reduction is to work with shorter time series that provide a proxy for the overall dataset, but allow for quicker stepping through the iterations.

Lastly, `__init__` calculates the fitness of the base case based on the method designated in `self.optimizationObjective`. The value, stored in `self.basePerformance` can be used as a benchmark for further optimization. 

**Note: it is not recommended to use `self.basePerformance` as direct benchmark for the results of the optimization run on shorter time-series. While trends relative to the base case may be discernible, absolute values may not be comparable. In the future, it would be recommended to calculate a proxy base case performance using the shorter time-series calculated in `getDataSubsets` and available in `self.abbrevDatasets` and `self.abbrevDataWeights`.**

# Optimization
The `doOptimization` method has to be called to dispatch an optimization run. `doOptimization` itself is an interface method, that reads the value in `self.searchMethod` and dispatches the desired actual optimization method. 

Currently only the an adapted hill climber method is implemented. Other methods should be considered while keeping in mind the significant run-time required per simulation (between 2 and 4 minutes per week of real-time at 1 Sample/second). 

## Adaptive Hill Climber
The hill climbing algorithm uses the history of fitness values, i.e., the renewable power penetration or fuel utilization, of its iterations to determine the direction in which to search for the next pairing of energy and power capacities. It does this until either, it has not found a better pairing for a set number of iterations (`convergenceRepeatNum`) or until a maximum number of iterations (`maxIterNum`) is reached. The history of the iterations is written to the object-wide variable `fl` (for fitnessLog) that can be accessed by the code that created the optimize object. 

The algorithm flow diagram is shown below. Key subroutines called by it are described further below. 

![hillClimber flow diagram](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/GBSOptimizer%20Flow%20Diagram%20-%20hillClimber.png)

### setupSet Method
Generates the specific `projectSetAttributes.xml` file, and the necessary folder in the project's output folder. Returns the name of the specific set and it's absolute path. Set naming follows the convention of 'Set[iterationNumber].[snippetNumber].[currentUNIXEpoch]', where iterationNumber is the current iteration of the of the optimizer.doOptimization-algorithm that is running (e.g., hillClimber), snippetNumber is the numerical identifier of the abbreviated data snippet, and the currentUNIXEpoch is the current local machine unix time to the second in int format.

**Inputs:**
* iterIdx: [int] current iteration of optimization algorithm
* setIdx: [int] numerical identifier of the snippet of time-series to be run here.
* identifier: [int] current local machine UNIX time to the second, could be any other integer
* eesIdx: [int] index of the ees to be added to the system, e.g., ees0. This is necessary should the system already have an ees that is not part of the optimization.
* eesPPa: [float] nameplate power capacity of the ees, assumed to be symmetrical in and out.
* eesEPa: [float] nameplate energy capacity of the ees, necessary to calculate ratedDuration, which is the actual parameter used in the setup.
* startTimeIdx: [int] index of the time stamp in the master-time series where the snippet of data starts that is to be run here.
* endTimeIdx: [int] index of the time stamp in the master-time series where the snippet of data ends that is to be run here.

**Outputs:**
* setPath: [os.path] path to the set folder
* setName: [String] name of the set

### getFitness Interface
This interface is described here [`getFitness.py`](../wiki/getFitness.py).

### getNextGuess Method
This method determines the next values for `essPPa` and `essEPa` that are to be tested in an iteration of the hill climber. It uses the historical fitness values from previous iterations and determines the direction of the steepest gradient away from the best fitness value. It then biases the random selection for new power and energy capacity values in the _opposite_ direction of the steepest gradient with the hope that this is the most likely direction to find a better value pair at. If new selections are outside of the constraints put on the search space, i.e., maximum and minimum power and energy capacities, and/or minimum duration (at the essPPa selected), it corrects selections back to the edges of the search envelope as set by the constraints. 

If the more iterations in the past the best found fitness lies, the stronger the random element in picking new values. The idea being that the algorithm might be stuck and larger jumps might get it unstuck.

**Note:** this approach to a hill climber was tested with several test functions (found in getFitness.py->getTestFitness). With these test functions the algorithm generally converges well. The caveat is, that recent results seem to suggest that the actual search space for the optimal energy storage may not be smooth, while the test cases used smooth test functions. This should be investigated further. 

**Inputs:**
* fl: [Pandas.DataFrame] fitnessLog with historical fitness values from previous iterations
* pBest: [float] explicit best power capacity value from previous iterations [from the iteration with the best overall fitness] 
* eBest: [float] explicit best energy capacity value from previous iterations [from the iteration with the best overall fitness] 
* iterNumParam: [float] parameter describing the randomness of the next value pair selection, fraction of iteration number and count since the last improved fitness value was found.

**Outputs**
newESSPPa, newESSEPa: [float] new pair of energy and power capacities to run the next iteration with
