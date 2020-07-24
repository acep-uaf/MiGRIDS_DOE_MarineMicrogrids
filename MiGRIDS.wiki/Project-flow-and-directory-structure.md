# Project Directory Structure
The following figure gives a sample project directory structure. The following section go into more depth for the files stored in each section. See the [Model Resources](Model-Resources-Package) page for more information of the setup files that go into a project directory. 

![Directory layout of a project. ](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/project_folder_structure.png)


## MiGRIDSProjects/ProjectName/InputData:
### /Components: 
All specific xml component descriptor files. For example, 'gen0Descriptor.xml'. These are created by running the function `fillProjectData.py`. This grabs user inputs from the `/Setup/UserInput` directory. 

### /Setup: 
Has the project setup xml file. This is created by running the function `fillProjectData.py`. This grabs user inputs from the `/Setup/UserInput` directory. 

### /Setup/UserInput:
This contains all the csv files currently used by `fillProjectData.py` to populate the xml file used as inputs to run the simulations and by `runDataImport` to import data from the input data files. These will be replaced by the GUI at some point. The files include
* `componentInformation.csv`: a list of components and their power levels. This is used to fill the `componentsNames` tag of the `projectSetup.xml` file. 
* `generalTagInformation.csv`: a list of tags, attributes and their values to fill into the `projectSetup.xml` file. 
* `timeSeriesInformation.csv`: connects columns in input data files with components specified in the `componentInformation` file. (Maybe this could be ported over to `componentInformation.csv`)
* `componentInformation.csv`: These have tag, attribute and value information to fill into the xml component descriptor files (save in `/Components`). For example `ees0TagInformation.csv`. 

### /TimeSeriesData/RawData:
Contains the raw timeseries files. 

### /TimeSeriesData/ProcessedData: 
Contains the processed time-series data files. These are created by running `runDataImport.py`. These are used to run the simulations. 

## MiGRIDSProjects/ProjectName/OutputData:
### /SetX:
Contains the setup and output data for a set of simulations. `X` refers to the set number. Files include:
#### `ProjectNameSetXAttributes.xml`: 
This file contains the changes to attributes in the xml component descriptor files in the project input (`MiGRIDSProjects/ProjectName/InputData/Components`) will be run for this set of simulations. Multiple values can be given for each attribute. Multiple values for one attribute must be separated by commas and no spaces. For example in the following code, multiple values are given for `ees0.PInMaxPa.value` and `ees0.ratedDuration.value`. The same value can be written to two attributes by writing the tag and attribute, separated by a period, to be copied in the value field. For example, in the following code, `ees0.POutMaxPa.value` will be identical to `ees0.PInMaxPa.value`. Simply copying the values `25,50,75` into the `ees0.POutMaxPa.value` field would result in `3*3=9` simulations for each possible combination of `ees0.POutMaxPa.value` and `ees0.PInMaxPa.value`. Attributes that require multiple values for one instance of a component (such as a fuel curve) cannot be changed here. A new component would need to be created and placed in `MiGRIDSProjects//ProjectName/InputData/Components`. 

       `<compName value = "ees0 ees0 ees0 "/> 

        <compTag value = "PInMaxPa POutMaxPa ratedDuration"/> 

        <compAttr value = "value value value"/> 

        <compValue value = "25,50,75 PInMaxPa.value 3600,1800,600,300,7200"/>`

It also lists changes to the xml project setup file (located in `MiGRIDSProjects/ProjectName/InputData/Setup`). Multiple values are not allowed to vary between simulations in one set. Multiple values are allowed when it is required by the attribute, such as `componentNames`. Running the function `generateRuns.py` will generate a set of simulation runs using the information in this file.
 
#### `setXComponentAttributes.db`: 
Running `generateRuns.py` will generate this SQL database with the table `compAttributes`. The columns in the table correspond to the component attributes that were changed from the base case values listed in the xml component descriptor files in `MiGRIDSProjects/ProjectName/InputData/Components`. Column headers list the component name, tags and attributes separated by `.`, for example `ees0.PInMaxPa.value`. The rows correspond to the run number. Each row has the values used for the attributes that are different from base case. The last two columns are called `started` and `finished`. A `1`/`0` in each column indicates the simulation run has/has not started and finished, respectively.

### /SetX/RunY/Components:
This contains the xml descriptor files for the components used this simulation run. These files are identical to the base case xml descriptor files, located in `MiGRIDSProjects/ProjectName/InputData/Components`, except for the changes specified in `/SetX/ProjectNameSetXAttributes.xml` and summarized for each run in `/SetX/setXComponentAttributes.db`. Files are named `componentNameSetXRunYDescriptor.xml`. For example `ees0Set2Run5Descriptor.xml`

### /SetX/RunY/OutputData:
This contains the net cdf time-series output files for this simulation run. They are named `componentNameVariableNameSetXRunY.nc` for example `gen0PSet2Run5.nc`. 

### /SetX/RunY/Figs:
This contains figures of plots of the time series for this run. 

# Project flow
This section goes over the flow of a project. See the [tutorials page](Project-tutorials) for projects that have already been set up for examples. 

## Import time series data
Run `runDataImport`. This processes raw time series data and saves the processed data into the `InputData/TimeSeriesData/ProcessedData`.

## Create component descriptors and project setup files
Run `fillProjectData`. This creates xml component descriptor files and saves them in `InputData/Components` . These represent the base case for each component that is currently in the grid as well as components that will be added in the simulations. 

Running `fillProjectData` also creates the xml project setup file which is saved in `InputData/Setup`. This gives the base case setup of the grid, including which components are run in the base case. 

## Grid Controller/Optimizer (not finished) 
This should create a set subdirectory in `OutputData` and create a `ProjectNameSetXAttributes.xml` file listing which components to run and any changes to their attribute values from the base case. Alternatively, to manually run simulations, create a `Set` directory in the `OutputData` folder and create and fill a `ProjectNameSetXAttributes.xml` file. 

## Generate the simulations
Run `generateRuns` to generate all the run subdirectories in `OutputData\SetX`. It populates them with xml component descriptor files with the values for that run. 

## Run the simulations
Run `runSimulation` to run each simulation. Multiple instances of this can be run in parallel. time series net cdf files are saved in the run directory. 

## Get meta data (not finished)
Run `getRunMetaData` to get a performance summary for the simulation run. This saves the results into an SQL database in the set directory named `setXResults.db`. Inside the database, there is a table called `Results` which has the column headers: 'Generator Import kWh','Generator Charging kWh','Generator Switching','Generator Loading','Generator Fuel Consumption kg','Wind Power Import kWh','Wind Power Spill kWh','Wind Power Charging kWh','Energy Storage Discharge kWh','Energy Storage Charge kWh','Energy Storage SRC kWh'. As other components are added to the simulation, they will need to be added to this table. A possible change in the future is to make separate tables for each component. The row indices correspond to the simulation run number. 

## Back to Controller/Optimizer 
The controller, optimizer or user can then decide which changes to make, create a new set directory with those changes, and repeat. 




