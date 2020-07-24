The `optimizerConfig.xml` file is the template for any configuration file for the optimization routines. The actual configuration file should be located in `MiGRIDSProjects/<myProjectName>/InputData/Setup/` and called `optimizerConfig<myProjectName>.xml`. Without such a file optimization fails. 

The following describes the various tags, their function and default values where warranted. 

# `optimizerConfig` Tag
Root tag wrapping all other tags

## `optimizationObjective` Tag
This contains the objective of the optimization. The value given determines which fitness function is actually called in [`getFitness.py`](../wiki/getFitness.py).

**Default value:** `"maxREContribution"` 

**Available choices:** 

* maxREContribution: looks for the EES size which maximizes renewable energy contribution
* minFuelUtilization: looks for the EES size which minimizes diesel fuel utilization of the generator fleet

If additional fitness methods are made available they need to be registered in the choices attribute of the optimizationObjective tag. 

## `optimizationConstraints` Tag
A container for various possible constraints on the optimization. Simulations failing to meet these constraints
are discarded. 

### `maxAnnualGenConfigChanges` Tag 
**NOTE: this tag currently is not used in the optimization.**

**Default value:** 2000

**Default setting:** `active="False"`
        
### `minESSP` Tag
Lowest ESS power capacity to be considered. Units: kW. If 'active' is true, enforce this constraint. Default value is 0.
**NOTE: the setting in this tag may be overridden by the selection in `optimizationEnvelopeEstimator`**

**Default value:** 0

**Default setting:** `active="True"`

### `maxESSP` Tag 
Highest ESS power capacity to be considered. Units: kW. If 'active' is true, enforce this constraint. Default value is 10000.
**NOTE: the setting in this tag may be overridden by the selection in `optimizationEnvelopeEstimator`** 

**Default value:** 10000

**Default setting:** `active="True"`

### `minESSE` Tag 
Lowest ESS energy capacity to be considered. Units: kWh. If 'active' is true, enforce this constraint. Default value is 0.
**NOTE: the setting in this tag may be overridden by the selection in `optimizationEnvelopeEstimator`**

**Default value:** 0

**Default setting:** `active="True"`

### `maxESSE` Tag
Highest ESS energy capacity to be considered. Units: kWh. If 'active' is true, enforce this constraint. Default value is 10000.
**NOTE: the setting in this tag may be overridden by the selection in `optimizationEnvelopeEstimator`**

**Default value:** 10000

**Default setting:** `active="True"`

## `optimizationEnvelopeEstimator` Tag
Configuration for [`getOptimizationBoundaries.py`](../wiki/getOptimizationBoundaries.py) interface. Based on the value given here the interface passes on to a specific boundary value estimation. Any new method to estimate boundaries needs to be registered with the `choices` attribute here. 

**Default value:** variableSRC

**Available choices:** 

* variableSRC: looks at the estimated SRC requirements to narrow down the ESS range of power and energy capacities , implemented in `calcSRCMethodBoundaries.py`. Additional configuration data for this method is provided in `variableSRCCongig`.
* noBoundaries: skips boundary calculation and merely uses the minimum and maximum values configured in the respective children of `optimizationContstraints`.

### `variableSRCConfig` Tag
Additional configuration passed through to calcSRCMethodBoundaries.

**`mode` Tag**
The attribute 'mode' describes how to reconcile the estimated envelope with the sizing constraints (minESSP/E, maxESSP/E); options are 'tight', which uses the narrower band of values, or 'relaxed' which uses the wider band of values. **NOTE:** this is currently not used. 

**`minDynSRC` Tag**
Fraction of total load that always should be kept as SRC. Default value is 0.15.

**`minDuration` Tag** 
Time in seconds that the energy storage has to cover SRC. Units: seconds. Default value is 60 seconds

**`minPercent` Tag**
Minimum percentile as a fraction that the energy storage has to be able to cover SRC. Units: none. Default value is 0.7. 

**`maxPercent` Tag**
Maximum percentile as a fraction that the energy storage has to be able to cover SRC. Units: none. Default value is 0.99.

**`maxMargin` Tag**
The margin put on the maximum power calculated as a fraction. Units: none. Default value: 1.10.
    
## `dataReductionMethod` Tag
Choices of methods used to reduce the long time series, in order to reduce algorithm run time. Only one method is implemented thus far. If additional methods are implemented they will have to be registered in the `choices` attribute.

**Default value:** RE-load-one-week

**Availble choices:** 

* RE-load-one-week: calls the reduction algorithm in [`getDataSubsetsRELoadOneWeek.py`](../wiki/getDataSubsetsRELoadOneWeek.py) 
* noReduction: skips data reduction and runs on the entire data set. **Not recommended.**

        
## `optimizationMethod` Tag
Selects from the available optimization algorithms.
**NOTE: the only functioning algorithm at this time is the `hillClimber` choice.** 

**Default value:** hillClimber

**Availble choices:** 

* hillClimber: selects an adaptive hill climbing algorithm. See `hillClimberConfig` for additional configuration.
* geneticAlgorithm: **Not implemented due to total compute time requirements. Here for illustration only.**

### `hillClimberConfig` Tag
Configuration parameters for the hillClimber algorithm. **Note: some configuration values are currently hardcoded, if these are desired to be configured they should be added here as child tags.**

**`minRunNumber` Tag**
Minimum number of iterations to dispatch. Default value is 3.  
            
**`maxRunNumber` Tag** 
Maximum number of iterations to dispatch. Default value is 50. **Note that 50 iterations might create considerable amounts of data and may require significant (>days) compute time**.


**`convergenceVariance` Tag **
Fraction of variance from best so far considered convergent. Default value is 0.1. **Note: this is not used currently. Convergence is only achieved if the exact best fitness value is found repeatedly.** 

**`convergenceRepeatNum` Tag** 
Number of consecutive repeats at convergence variance to terminate. Default value is 3. 

**`dispatchFullRunAtConvergence` Tag** 
If true, the best found configuration is dispatched for a full length simulation. Default value is False. **Note: due to the total time requirement for dispatch of a full simulation, this is currently not implemented.** 

### `geneticAlgorithmConfig` Tag
**Place holder only. Note implemented.**
            
