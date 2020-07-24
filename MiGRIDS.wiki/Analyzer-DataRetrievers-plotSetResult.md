The `plotSetResult` module contains the function `plotSetResult` that will plot a single result for a set of simulations. The png and pdf plots will be saved in the `OutputData/Setx/figs`, where `x` is the set identifier. [plotSetResultSandbox](TestScripts-plotSetResultSandbox) contains a sample implementation. 

# Inputs
**plotRes**: the database column header of the variable to plot.

**plotAttr**: The simulation attribute to be plotted against. This is the column header in the database as well as the tag and attribute from the component or setup xml file.

**otherAttr**: The other component or setup attributes to have fixed values in the plot. If not specified, all values for the attribute will be plotted as multiple lines.

**otherAttrVal**: The values of the 'otherAttr' to plot. It should be given as a list of lists, corresponding to otherAttr.

**removeOtherAttr**: a list of other attributes to remove from the legend. These are for attributes that only have one value for every other combination of values.

**baseSet**: the set identifier of the base set. If left as '', then no base case is plotted.

**baseRun**: the run number of the base set. If left as '', then no base case is plotted.

**subtractFromBase**: 0  - do not subtract or add, but if base case is specified, place at the beginning; 1 - subtract value from base -> decrease from base case; 2 - subtract base from value -> increase from base case

**plotAttrName**: the desired x axis label

**otherAttrNames**: a dict of the other attribute variable names that will go in the legend and the names desired to be used in the legend

**saveName**: the name to save the plots as. If left '', then a default naming convetion will be used. 
