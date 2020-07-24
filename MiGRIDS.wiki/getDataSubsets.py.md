This method contains the interface to retrieve a representative subset of data to run the optimization algorithm with. 

The configuration of the actually connected calculation method should be declared in the pertinent [`optimizerConfig.xml`](../wiki/optimizerConfig.xml) file, in the tag `dataReductionMethod`.

Note: new entries added to `dataReductionMethod` and implemented as methods need to be registered in this interface to become available.

## Method inputs
* dataframe: [Pandas.DataFrame] containing the dataset to down-select from. How this dataframe is structured does not matter to the interface, but does matter for actually implemented methods. 
* method: [String] data reduction method. Identifies the actual implementation to be used. 

## Outputs
* datasubsets: [Pandas.DataFrame] bin for selected data subsets. This DataFrame has to be structured such that the methods connected in the optimize.doOptimization interface can interpret them. 
* databins: [Pandas.DataFrame] bins describing how the original data could best be mapped to the reduced data in datasubsets. 

## Exception
May terminate with ValueError is the string in `method` is unknown. 

Below is the flow diagram for the interface. 

![getDataSubsets Flow Diagram](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/GBSOptimizer%20Flow%20Diagram%20-%20getDataSubsets.png)
