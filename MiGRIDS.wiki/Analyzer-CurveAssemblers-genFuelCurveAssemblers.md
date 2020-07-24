The class `genFuelCurveAssembler` contains methods to build a dense fuel curve for diesel generators based on sparser information provided in `genDescriptor.xml`.  There the fuel curve contains tuples of tags, pPu (power in P.U. referenced to nameplate capacity) and massFlow in kg/s. Here the intent is to provide a density of points such that there is a fuel consumption data point for each 1 kW increment in power level. For practical reasons, the pPu output curve does include overload values, which exhibit a linear extension of the fuel consumption given for pPu = 1. Note that the fuel consumption data input assumes that corrections for fuel temperature, fuel type, etc. have already been performed.

# Input Variables
* __fuelCurveDataPoints__: # Data points give in genDescriptor.xml, list of tuples, [kW, kg/s]

* __genOverloadPMax__: Maximum overload capacity [kW]. This is used to provide a maximum x-coordinate for the fuel curve

# Output Variables
* __fuelCurve__: The dense fuel curve with units [kW, kg/s]

* __fuelCurveInt__: The dense fuel curve, but with integer values only. Fuel consumption values to be multiplied by 10,000.

# Methods
**checkInputs(self)**: Makes sure data inputs are self-consistent. **Does not** check for physical validity of data.

raises ValueError: for various data inconsistencies or missing values.

does not return anything. 

**cubicSplineCurveEstimator(self, loadStep = 1)**: calculates a cubic spline for the given data points in fuelCurveDataPoints. `loadStep` is the interval between power values in the resulting power curve. 

**linearEstimator(self, loadStep=1)**: calculates a linear interpolation for the given data points in fuelCurveDataPoints. `loadStep` is the interval between power values in the resulting power curve. 


