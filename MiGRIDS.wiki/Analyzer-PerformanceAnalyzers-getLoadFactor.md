 Calculates the load factor for all generator power channels provided as input, and a cumulative load factor for the sum of all channels.

# Inputs
**genAllP**: [DataFrame] columns are 'time' and 'genXP' channels where X is the specific generator number
**genAllPOutMaxPa**: [DataFrame] 'genX' is index, single column 'POutMaxPa' is nameplate power of each gen
# Outputs
**genAllPPu**: [DataFrame] same format as genAllP, but with all power values relative to POutMaxP for each specific generator and a 'genTotPPu' column with load factor relative to total nameplate capacity.
 