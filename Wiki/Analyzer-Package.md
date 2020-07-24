This package contains routines to analyze input and output data, convert units, and derive compliant data formats for the Model Package requirements from other data, e.g., fuel and power curves. 

The package is organized into the following sub-packages:
* [CurveAssemblers](Analyzer-CurveAssemblers-Package): contains routines to develop smooth curves from input data such as data points for a wind power curve.
* [DataRetrievers](DataRetrievers): contains routines to retrieve data from simulation input and output data files. 
* [DataWriters](Analyzer-DataWriters): contains routines to write datafiles. 
* [PerformanceAnalyzer](Analyzer-PerformanceAnalyzers): contains routines to get performance metrics and overall results from data files. 
* [UnitConverters](Analyzer-UnitConverters-Package): contains routines to do unit conversions, as well as to data corrections, e.g., volume to mass flow conversion corrected for temperature effects. 
