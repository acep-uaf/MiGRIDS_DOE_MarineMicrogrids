This file describes the default units, scale, offset and datatype used by the different types of data in the model. 

### `P` tag
Real power. 

***Attributes:***

`units`: kW

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `Q` tag
Reactive power. 

***Attributes:***

`units`: kvar

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `S` tag
Apparent power. 

***Attributes:***

`units`: kVA

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `WS` tag
Wind Speed. 

***Attributes:***

`units`: m/s

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `Tstorage` tag
Internal temperature of thermal storage. 

***Attributes:***

`units`: K

`scale`: 1,000,000 

`offset`: 0 

`datatype`: int32

### `Tambient` tag
Ambient temperature. 

***Attributes:***

`units`: K

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `time` tag
time stamps of data. 

***Attributes:***

`units`: seconds since January 01 1970 (UTC)

`scale`: 1 

`offset`: 0 

`datatype`: int32

### `FF` tag
Fuel flow .

***Attributes:***

`units`: kg/s

`scale`: 10,000 

`offset`: 0 

`datatype`: int32