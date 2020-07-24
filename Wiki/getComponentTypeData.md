Retrieves all meta-data for a given component class from the descriptor xml files.

# Inputs
**projectPath**: [string] path to the projects root folder

**projectName**: [string] the project name as it is used in <projectName>Setup.xml

**componentType**: [String] the abbreviated component type descriptor, e.g. 'gen' to retrieve all generators

# Outputs
**componentData**: [DataFrame] Contains component information with XML tags as columns and component names (gen1, gen2, etc) as index.