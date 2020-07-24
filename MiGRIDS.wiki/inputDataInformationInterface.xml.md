the general input data information interface is found in `inputDataInformationInterface.xml`. The following tags are described in this file and should exist in any child. 

## Root tag - `project`

The root tag has be present in any input Data description. 

**Attributes**:
`name`: the project name

### `inputFileDir`tag
Describes the absolute path to the directory where the input files are located. 

**Attributes:**

`value`: the directory absolute path. Default value is ''. 

### `inputFileType`tag
Describes the file types of the input data files. For example '.CSV'. 

**Attributes:**

`value`: the file type. Default value is ''. 

### `inputFileFormat`tag
Describes the format that the input files are in. This includes formatting specific to certain data sources where a script has been specifically generated to deal with the data. For example 'AVEC'. If this is not specified then it will assume that the data files are organized in a data table with a header at the top.

**Attributes:**

`value`: the file format. Default value is ''. 

### `componentChannels` tag
Describes the input data channels corresponding to grid components to read into the simulation. The tuple `headerName` is the names or indices of the columns in the input data files. The tuple `componentNames` contains the corresponding names in the componentDescriptor files. The tuple `componentAttribute` describes what attribute of the component is stored in the data channel and what its units are. 

**Attributes:**

#### `headerName`

`value`: The input file header names. Default is ''.

#### `componentName`

`value`: the corresponding name in the component descriptor files. 

#### `componentAttribute`

`value`: what is being measured. Possible values for componentAttribute include 'P' (real power), 'Q' (reactive power), 'S' (apparent power), 'pf' (power factor), 'V' (voltage), 'I' (current), 'f' (frequency), 'Tamb' (ambient temperature), 'Tstorage' (internal temperature for thermal storatge), 'WS' (windspeed), 'IR' (solar irradiation), 'WF' (water flow), 'Pavail' (available real power), 'Qavail' (available reactive power), 'Savail' (available apparent power). Default is ''. 

`unit`: the unit that the component attribute was measured in. Available units for power include 'W', 'kW', 'MW', 'var', 'kvar', 'Mvar', 'VA', 'kVA', 'MVA'. Available units for voltage includes 'V' and 'kV'. Available units for current are 'A' and 'kA'. Available units for frequency is 'Hz'. Available units for temperature are 'C', 'F' and 'K'. Available units for speed are 'm/s', 'ft/s', 'km/hr' and 'mi/hr'. Available units for irradiation is 'W/m2'. Available units for flow include 'm3/s', 'L/s', 'cfm' and 'gal/min'. Default is ''. 

### `dataChannel` tag

Describes the name or index of the data channel with the timestamps. 'value' is the name or index. 'format' is the format of the date, for example 'ordinal'.

**Attributes:**

`value`: the input data channel with the date. Default value is ''. 

### `timeChannel` tag

Describes the name or index of the data channel with the times of day. 'value' is the name or index. 'format' is the format of the time, for example 'HH:MM:SS:MS'. Also accepted is time as a fraction of 24 hours ('excel'). If this is not set, then the timestamps will be assumed to be incorporated into the dataChannel.

**Attributes:**

`value`: the input data channel with the time. Default value is ''. 

`format`: the format of the time data. Default value is ''. 

### `realLoadChannel` tag

Describes the name or index of the total grid real load. If this is not set, then the load will be calculated as the difference between all input generating unit data channels and input controllable loads data channels.

**Attributes:**

`value`: the input data channel with the real load. Default value is ''. 


### `minRealLoad` tag

Describes the minimum real load expected.

**Attributes:**

`value`: Default value is ''. 


### `maxRealLoad` tag

Describes the maximum real load expected.

**Attributes:**

`value`: Default value is ''. 


### `imaginaryLoadChannel` tag

Describes the name or index of the total grid imaginary load. If this is not set, then the load will be calculated as the difference between all input generating unit data channels and input controllable loads data channels.

**Attributes:**

`value`: the input data channel with the imaginary load. Default value is ''. 

### `timeStep` tag

Describes the desired timestep to be used in the simulation. The data will be resampled to this value. Default is 1 second.

**Attributes:**

`value`: desired time step. Default value is 1. 

`unit`: seconds
