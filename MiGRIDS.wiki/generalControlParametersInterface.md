The general component description interface is found in `generalControlParametersInterface.xml`. The following tags are described in this file and should exist in any child. 

## Root tag - `generalControlParameters`
The root tag has to be present in any general control parameters implementation. 

### `prevLoadTime` tag
The `prevLoadTime` tag describes how far back the is used to assess previous load levels in order to predict future load levels. The assessment method is defined by parameter `prevLoadAss`. 

***Attributes:***

`value`: Default is 5 min. 

`unit`: Minutes. 

### `prevLoadAss` tag
The `prevLoadAss` tag is the method used to assess the previous load in order to predict what the future load will be. 'value' is a string. Options include 'average', 'weightedAverage' and 'trend' . Default is 'average'. This is just the average of the previous period described by 'prevLoadTime'.

***Attributes:***

`value`: Default is 'average'. 

`unit`: NONE. 

### `lowerCut` tag
The `lowerCut` tag is the cut off frequency used in the FIR filter. A value of zero indicates no smoothing.  This is used in conjunction with the number of taps specified in the control descriptions for each component. 

***Attributes:***

`value`: Default is 0 Hz. 

`unit`: Hz. 

