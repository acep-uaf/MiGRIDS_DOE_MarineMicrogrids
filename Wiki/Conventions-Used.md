# File and Variable Naming
File and variable naming follows camel case rules and uses the abbreviations defined in the general naming convention developed by ACEP. A copy of the convention can be found [here](/acep-uaf/MiGRIDS/blob/master/netCDF%20Naming%20Conventions.pdf).

# Format of netCDF files
netCDF files shall be formatted following ACEP netCDF guidelines where ever practical. Omission of some information may be allowable. However, all data files should contain the tags requested by the convention for consistency. A copy of the convention can be found [here](/acep-uaf/MiGRIDS/blob/master/netCDF%20convention.xlsx) - Note that GitHub will not render this file, download to view.

# Units
Units of all internal variables shall be SI, or acceptable extensions of SI as per [NIST](https://physics.nist.gov/cuu/Units/index.html). For end-user interaction an option of conversion to non-SI units will be given for such variables commonly used in non-SI format. 

# Discretization of units
In some cases it is more efficient to work with integers instead of floats within the code, or it may be more efficient to discretize units so that not too many points of a function have to be pre-calculated and carried in memory. For these considerations, the following conventions are used.

## Power (real, reactive and apparent)
The discretization of real, reactive and apparent power levels is done to the nearest kW, kvar, and kVA respectively. This recognizes that smaller resolution of power levels generally is not used (or measured) in utility-grade systems. 

## Mass flow
Mass flow for fuel consumption utilizes SI units,  kg/s. For smaller generator sets, the actual values can be small (Order(-4)). Thus, when using the integer-only array of the fuel curve (generated in [genFuelCurveAssembler](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Analyzer/CurveAssemblers/genFuelCurveAssembler.py)) a multiplier of 100,000 is used. 
