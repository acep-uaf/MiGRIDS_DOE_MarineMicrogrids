This method represents an interface for optimization boundary calculation. Connected methods are meant to narrow down the ranges of power and energy capacity of an energy storage system that should be considered during optimization in order to reduce compute time and help optimization algorithms to find physically realistic solutions. 

The configuration of the actually connected calculation method should be declared in the pertinent [`optimizerConfig.xml`](../wiki/optimizerConfig.xml) file, in the tag `optimizationEnvelopeMethod`. 

**Note:** new entries added to `optimizationEnvelopeMethod` and implemented as methods need to be registered in this interface to become available. 

## Method inputs
* boundaryMethod: [String] the actual method to be used 
* time: [Pandas.Series] the variable containing all time stamps
* firmLoadP: [Pandas.Series] the firm real load associated with each time stamp 
* varLoadP: [Pandas.Series] the variable real load associated with each time stamp
* firmGenP: [Pandas.Series] the firm real power generated at each time stamp 
* varGenP: [Pandas.Series] the variable real power generated at each time stamp
* otherContraints: [list(str)] bin for additional configuration of attached implemented methods. 

## Outputs
* minESSPPa: [float] minimum ESS real power capacity, kW.
* maxESSPPa: [float] maximum ESS real power capacity, kW. 
* minESSEPa: [float] minimum ESS energy capacity, kWh.
* maxESSEPa: [float] maximum ESS energy capacity, kWh. 

## Exception
May terminate with UserWarning if input string `boundaryMethod` does not contain a valid entry. 

The below flow diagram depicts how the interface works. 

![getOptimizationBoundaries flow diagram](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/GBSOptimizer%20Flow%20Diagram%20-%20getOptimizationBoundaries.png)
