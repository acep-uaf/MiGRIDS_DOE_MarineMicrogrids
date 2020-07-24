The `wtgCurveAssembler` module contains a class that assembles the necessary methods to estimate a wind turbine power curve at 0.1 m/s wind speed intervals from power data given at a lesser number of wind speed data points. 

Several methods are useful in estimating power curves for wind turbines. For now, this module only implements
calculation of via cubic splines. For a source discussing splines and other methods of estimation see [Sohoni, Gupta and Nema, 2016](https://www.hindawi.com/journals/jen/2016/8519785/)

**Assumptions**:
    
* __Inputs__: data used as input is already from a cleaned up power curve. This tool is not intended to produce a power curve from operational time-series data, which would require cleaning and filtering. Thus, __it is required that for each wind speed value one and only one power value exists__. That is, temperature compensations, if desired will have to be handled separately.

* __cutOutWindSpeedMax__ describes the point beyond which the turbine is shut off for protection. Right at this point, it produces power at nameplate capacity levels (unless a specific and different value is given). Beyond this point the turbine is stopped and P = 0 kW.

* __cutOutWindSpeedMin__ describes the point where the turbine does not produce power any longer, e.g. P = 0 kW at this wind speed.

* __cutInWindSpeed__ is the minimum wind speed at which a stopped turbine starts up. At this point power production is immediately greater zero, i.e. cutOutWindSpeedMin < cutInWindSpeed.

# `WindPowerCurve` class
The WindPowerCurve class contains methods to determine a wind power curve from data provided in the wtgDescriptor.xml file. 

**Input Variables**: 

* __powerCurveDataPoints__: list of tuples of floats, e.g., [(ws0, p0), ... , (wsN, pN)], where ws and p are wind speed (m/s) and power (kW) respectively.

* __cutInWindSpeed__: float, wind speed at which a stopped turbine begins to produce power again, m/s

* __cutOutWindSpeedMin__: float, the wind speed at which the turbine does not produce power anymore due to lack of wind power, units are m/s

* __cutOutWindSpeedMax__: float, the wind speed beyond which the turbine is stopped for protection, units are m/s.

* __POutMaxPa__: float, nameplate power of the turbine, units are kW.

**Output Variables**:

* __powerCurve__: list of tuples of floats, with a defined range ws = 0 m/s to ws = cutOutWindSpeedMax and some fixed points powerCurve = [(0,0), (cutOutWindSpeedMin, 0), ..., (cutOutWindSpeedMax, PCutOutWindSpeedMax), (>cutOutWindSpeedMax, 0)]
Wind speeds are reported in increments of 0.1 m/s, power values are in kW.

* __powerCurveInt__: list of tuples of integers derived from the float values in `powerCurve` by rounding to the nearest integer and typecasting from float to int. Wind speed data, to preserve resolution, is multiplied by 10, e.g., 3.6 m/s is now reported as 36, and power data is rounded to the next kW. 
     

**Methods**:

* __checkInputs__: **Internal method**. Checks input data for basic consistency and ensures that there are no duplicate data points which could interfere with some of the curve approximations that assume there is a unique power value for each wind speed. 

* __cubicSplineCurveEstimator__: calculates a cubic spline for the given input data set with the constraints given by the power curve, cut-in and cut-out wind speeds, a condition that the boundary conditions be `clamped`, i.e., that the first derivative at the end points be zero, and with the condition that the spline not extrapolate to points outside the input interval. This method uses [`scipy.interpolate.CubicSpline`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.interpolate.CubicSpline.html) for the cubic spline calculation. 