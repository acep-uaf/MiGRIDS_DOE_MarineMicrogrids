This module contains an assembly of functions used for unit conversion. The method name corresponds directly with the conversion, e.g., `gallons2liter` converts US gallons to liters.

# Methods
**gal2l(gallon)**: Converts US gallons to liters using the conversion: 1 US gallon = 3.78541 l


**l2gal(liter)**: Converts liters to US liquid gallons using the conversion: 1 liter  = 0.264172 gallons

**l2cubicMeter(liter)**: Converts liters to cubic meters using the conversion: 1 l = 0.001 m^3

**w2kw(w)**: Converts watts to kW using the conversion: 1 kW = 1000 W

**mw2kw(mw)**: Converts MW to kW the conversion: 1 MW = 0.001 kW

**c2k(c)**: Converts degrees C to degrees K using the following conversion: 1 K = C + 273.15

**f2k(f)**: Converts degrees F to degrees K using the following conversion: 1 K = (K + 459.67)*(5/9)

**lph2kgps(lph)**: Volume to mass flow converter Liters/hour to kg/s. This converter works for **diesel fuel at room temperature only**. Do not use for any other liquids without adjusting the conversion factor. The conversion is 1 kg/s = 0.875/3600 l/h.