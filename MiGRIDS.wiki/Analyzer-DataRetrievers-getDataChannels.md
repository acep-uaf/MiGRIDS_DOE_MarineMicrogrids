Retrieves data channels based on list of channels requested. ASSUMES that all channels have a uniform time vector.

# Inputs
**projectPath**: [string] path to the projects root folder

**dataPath**: [string] path to the specific data folder

**channelList**: [List of strings] explicit list of channels to retrieve

# Outputs
**dataPackage**: [DataFrame] package of channels, first column is time, rest follows 'channelList', index is ints
   