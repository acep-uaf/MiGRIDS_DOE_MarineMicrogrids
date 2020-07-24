Calculates the total number of configuration changes for the diesel power house. This assumes that a 'genP' channel reading 0 kW means that generator is offline. If the channel reads non-zero and positive the generator is assumed to be online.

Note: if negative values are present, they are deleted [set to 0]

# Inputs
**genAllP**: [DataFrame] the real power channels for the generator fleet. Function checks if a time channel is included and ditches it if needed.
# Outputs
**genConfigDeltaTot**: [int] total number of generator configuration changes.
    