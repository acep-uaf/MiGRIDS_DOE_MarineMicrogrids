This module contains the function `getFuelUse` to calculate the fuel consumption for each generator and time step given.

FUTUREFEATURE: currently just tosses generator loads greater than POutMaxPa and replaces them with fuel use at 'POutMaxPa'. Better handling of overloads would be good.

# Inputs
**genAllP**: [DataFrame] individual genXP channels and time channel, index is integers numbering samples

**fuelCurveDataPoints**: [DataFrame] index is generator names, columns are 'fuelCurve_pPu' and 'fuelCurve_massFlow', 'POutMaxPa'

**interpolationMethod**: the interpolation method used for the fuel curve is indicated here. 'linear', 'cubic' or 'none' are valid inputs. 'none' indicates no interpolation is needed, the input fuel curve will be used to calculate fuel consumption. Default value is 'linear'.

# Outputs
**genAllFuelUsed**: [DataFrame] contains individual genX fuel used [kg] and time channel, index is integers

**fuelStats**: [DataFrame] fuel stats for each gen and totals
    