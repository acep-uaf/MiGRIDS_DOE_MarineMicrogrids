The general component description interface is found in `componentDescriptorInterface.xml`. The following tags are described in this file and should exist in any child. 

There are active tags that are currently implemented in the tool and inactive tags that are not yet implemented but allow for future expansion and functionality. 

# Active tags

## Root tag - `component`
The root tag has to be present in any component description. 

**Attributes**:
`name`: the name under which the particular component is known.

### `PInMaxPa` tag
Describes the maximum real power the component can receive from the grid. This should be zero if the unit is a source.

**Attributes:**

`value`: the actual nameplate value. Use an integer number. Default value is 0. 

`units`: units of the `value` attribute. This is a string. Default is kW.

### `POutMaxPa` tag
Describes the maximum real power the component can deliver to the grid. This should be zero if the unit is a sink.

**Attributes:**

`value`: the actual nameplate value. Use an integer number. Default value is 0. 

`units`: units of the `value` attribute. This is a string. Default is kW. 




# Inactive tags

### `type` tag
The type tag describes the general component type, and hence it's general capabilities. The options are `sink`, `source`, `sink-source` and `grid`.

**`sink`**: this is a component that consumes electric energy provided to it by the grid. A sink may just consume energy directly, or it may have a storage system attached to it that does not allow for re-extraction of electrical energy. 

**`source`**: this is a component that provides electric energy to the grid. A source may be connected to a form of energy storage that cannot be replenished by the grid, e.g., a fuel tank, or may use a 'fleeting' resource to provide power, e.g., wind or solar power. 

**`sink-source`**: this is a component that can provide or consume electric energy and thus has some form of energy storage capacity attached that allows input **and* extraction of electrical energy. 

**`grid`**: this is a component that conducts electric energy.

 

### `QInMaxPa` tag
Describes the maximum reactive power the component can receive from the grid. This should be zero if the unit is a source.

**Attributes:**

`value`: the actual nameplate value. Use an integer number. Default value is 0. 

`units`: units of the `value` attribute. This is a string. Default is kvar. 


### `QOutMaxPa` tag
Describes the maximum reactive power the component can deliver to the grid. This should be zero if the unit is a sink.

**Attributes:**

`value`: the actual nameplate value. Use an integer number. Default value is 0. 

`units`: units of the `value` attribute. This is a string. Default is kvar. 

### `isVoltageSource` tag
Defines if this unit can provide var-control. That is, can act as a voltage reference for other units.

**Attributes:**

`value`: TRUE if voltage source. FALSE otherwise (default). 

### `isFrequencyReference` tag
Defines if this unit can provide a frequency reference for the grid. Together with the `isVoltageSource` and `isLoadFollowing` tag (all three have to be true) this comprises a 'grid forming' service to the grid. 

**Attributes:**

`value`: TRUE if the unit can provide reference frequency. FALSE otherwise (default). 

### `isLoadFollowing` tag
Defines if the unit can follow demand within its envelope of nameplate real/reactive power capabilities. Note that sinks may also be able to load follow, e.g. a frequency aware secondary load controller. Thus, not all load following units may be grid forming. Load following generally is expected to be an autonomous function of local controls based on frequency or voltage measurements. 

**Attributes:**

`value`: TRUE if load following capable. FALSE otherwise (default). 

### `isCurtailable` tag
Defines if the output/input of the component can be clamped to a maximum value that is less than the respective nameplate maximum regardless of resource availability. 

**Attributes:**

`value`: TRUE is curtailment capable. FALSE otherwise (default).

### `isThreePhase` tag
Describes if the unit is three phase (either 3 or 4 wire). 

**Attributes:**

`value`: TRUE if three phase (default). FALSE otherwise. 

### `isDelta` tag
Describes if the unit is delta connected. 

**Attributes:**
`value`: TRUE if delta connected (default). FALSE if wye connected. 

### `acConnectionType` tag
Describes which phases are connected, if a neutral is present, etc. 

**Attribute:**

`value`: default is 0, which means that no AC connection exists (DC system that requires an inverter to grid connect). 1: phase A and neutral; 2: phase B and neutral; 3: phase C and neutral; 4: phase A and B and neutral; 5: phase A and C and neutral; 6: phase B and C and neutral; 7: phase A, B, C, and neutral without ground bonding; 8: phase A, B, C, and bonded neutral; 9: DC connection. 

`unit`: NONE.

### `dcConnectionType` tag
Describes the type of DC connection of the component, if any. 

**Attributes:**

`value`: default is 0, which means no DC connection exists. 1: zero potential reference at negative pole; 2: zero potential reference centered between positive and negative pole; 3: floating system (only potential difference between poles matters). 

`unit`: NONE.

### `VAcNom` tag
Describes the nominal AC connection voltage to the grid. In three-phase systems use P-P voltages. 

**Attributes:**

`value`: the nominal AC connection voltage. Default is 480 VAC. 

`unit`: Units are V. 

### `faultCurrent` tag
Describes the amount of fault current that can be supplied  per ms. Fault current units are in P.U. of nameplate current and are described by the tuple 'iPu'. Fault current values are defined for the number of ms they can be sustained, described by the tuple 'ms' (16.7 ms per 60 Hz cycle). 

**Attributes:**

#### `ms`: 

`value`: The number of ms that the fault current can be sustained for. Default is 5 ms. 

`unit`: Units are ms. 

#### `iPu`

`value`: The fault current. Default is 1 pu. 

`unit`: Units are per unit of nameplate current capacity, pu. 

### `overLoad` tag
Describes the amount of over load that can be supplied per hour. Over load units are in P.U. of nameplate power and are specified by the number of hours they can operate at. It is described by the tuples 'hr' (time with units hours) and 'pPu' (P.U. of nameplate capacity).

**Attributes:**

#### `hr`: 

`value`: The number of hours that the over load can be sustained for. Default is 1 hr. 

`unit`: Units are hr. 

#### `pPu`

`value`: The over load. Default is 1 pu. 

`unit`: Units are per unit of nameplate power capacity, pu. 

### `maxMeanLoad24HrPu` tag
Is the the maximum average loading the component is rated for in a 24 hour period. For example, for diesel generators, this rating is different for Prime, Standby and Continuous rated engines and between manufacturers. The ISO-8528-1 specification for a Prime generator is 0.7.

**Attributes:**

`value`: Default is 1 pu. 

`unit`: Units are in per unit of nameplate power capacity, pu. 

### `heatingPowerRequirement` tag
Describes the thermal power required to keep the component warm, if required. For example diesel generators in hot standby need to be heated. It is described by three tuples: 'tempAmb' is the ambient (outdoor) temperature in Kelvin. 'tempHeatingMin' is the minimum temperature required for the heating fluid used to heat the component. 'pt' is the thermal power consumption in kW. This will be supplied by whatever excess heat is available. 

**Attributes:**

#### `tempAmb`: 

`value`: Default is 298 K. 

`unit`: Units are K. 

#### `tempHeatingMin`

`value`: Default is 298 K. 

`unit`: Units are K.

#### `pt`:

`value`: The thermal power consumption. Default is 0 kW. 

`unit`: Units are kW.

### `heatRecovery` tag
Describes the usable heat that comes off of the component per power output.  It is described by the tuples 'pPu' (power), 'pt' (thermal power) and 'temp' (the temperature of the heat exchange fluid) Units for power are P.U. of nameplate power capacity, for heat output are thermal kW (not electric) and for temperature are Kelvin. Default is to have a data point at 0 and 1 P.U. power output of no heat recovery and at room temperature.
**Attributes:**

#### `pPu`: 

`value`: Default is 0 and 1 pu. 

`unit`: Units are in per unit of nameplate power capacity. 

#### `pt`

`value`: Default is 0 and 0 kW. 

`unit`: Units are kW.

#### `temp`:

`value`: Default is 298 K.

`unit`: Units are K.



