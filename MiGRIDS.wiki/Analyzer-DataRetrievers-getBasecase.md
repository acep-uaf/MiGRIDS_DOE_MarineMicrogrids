Retrieve base case data and meta data required for initial estimate of search space boundaries and data sparsing.

FUTUREFEATURE: Note that this does its own load calculation, which may be redundant or differ from load calculations done in the InputHandler. This should be revisited in the future.

# Inputs
**projectName**: The name of the base case project. 

**rootProjectPath**: is the directory where the base case project is located. 

# Outputs
**time**: [Series] time vector
**firmLoadP**: [Series] firm load vector
**varLoadP**: [Series] variable (switchable, manageable, Dispatchable) load vector
**firmGenP**: [Series] firm generation vector
**varGenP**: [Series] variable generation vector
**allGenP**: [DataFrame] contains time channel and all generator channels.
