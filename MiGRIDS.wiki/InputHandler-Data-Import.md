## `mergeInputs` 

### Description

Merge inputs handles data import from various directories and merges these data in to a single dataframe. During the process it calls the appropriate [read method](InputHandler-Read-Data), and [processes](InputHandler-Process-Data) the dataframe.
### Inputs
    **inputDictionary**: [Dictionary] a dictionary of input information pertaining to a set of files that will be imported. Input dictionary must contain a fileLocation attribute, fileType, headerNames, newHeaderNames, componentUnits,
### Outputs
    pandas.DataFrame a dataframe of resulting imports.
    List of components in the resulting dataframe.
