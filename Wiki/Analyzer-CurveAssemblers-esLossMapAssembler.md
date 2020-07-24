The class `esLossMapAssembler` module contains a class that assembles the necessary methods to estimate a loss map for an energy storage unit. It can be electrical or thermal. 

# Input Variables
* __lossMapDataPoints__: # list of tuples for a loss map. (power [pu], SOC [pu], loss [pu of power], ambient temperature [K])

* __pInMax__: Maximum output power [kW]. This is the will be the upper limit of the power axis
       
* __pOutMax__: Maximum input power [kW]. This is the will be the upper limit of the power axis
       
* __eMax__: Maximum energy capacity in kWs

# Output Variables
* __lossMap__: The dense lossMap with units [kW, kg/s]

* __lossMapInt__: The dense lossMap, but with integer values only.

* __P__: Loss map array power vector

* __E__: Loss map array energy vector

* __Temp__: loss map array temperature vector

* __loss__: loss map array with dimensions P x E 

* __maxDischTime__: an array, with same dimensions as the loss map, with the max amount of time that the es can charge or discharge at a given power for starting at a given state of charge
 
# Methods
**checkInputs(self)**: Makes sure data inputs are self-consistent. **Does not** check for physical validity of data.

raises ValueError: for various data inconsistencies or missing values.

does not return anything. 

**linearInterpolation(self,chargeRate, pStep = 1, eStep = 3600, tStep = 1)**: This performs a linear interpolation on the input data and generates the output data. 
**chargeRate** is the maximum fraction of the remaining energy storage capacity that can be charged in 1 second, or remaining energy storage capacity that can be discharged in 1 second, units are pu/sec. **pStep**, **eStep** and **tStep** are the steps to be used in the loss map for power, energy and temperature. Units are kW, kWs and K.

