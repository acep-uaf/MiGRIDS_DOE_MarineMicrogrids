# Overview of the Software Packages
The MiGRIDS tool software is comprised of six distinct packages that interact to provide custom energy storage sizing for islanded hybrid-diesel microgrids. Each of the packages has their own wiki page and sub-pages to provide detailed information. Here, only an overview is given. 

![Major software packages and flow of data and control](https://github.com/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/MiGRIDS%20Packages.png)

The above images shows the six major software packages and the flow of data (solid lines) and control (dashed lines). 

![Typical System Flow](https://github.com/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/MiGRIDS%20Flow%20-%20Conceptual%20-%20Page%201.png)

The above flow chart shows the typical flow through the major functional packages, without utilizing the  InputHandler Package, which initially deals with incoming data and project setup into the Project folder. The Project folder is the repository for project specific input and output data. 

## InputHandler Package
This package handles data sources and ensures proper conversion to defined netCDF format for use as model inputs. It acts as an interface between any kind of reasonable data source format and the internal format for data handling. Model input requires continuous timeseries parameters at equal time intervals. The input handler fills any missing values with suitable values found elsewhere in the dataset. If suitable values are not found, langevin estimation may be used to simulate small chunks of data dependent on descriptive metrics of the surrounding data. Wind data from MET towers provided as time interval mean and standard deviation may also be upsampled to smaller time intervals using langevin estimation to create a timeseries windspeed distribution.

## Model Package
This package contains the main time-series energy balance model. Sub-packages contain component and control descriptions for various units, dispatch controllers, etc. 

## Analyzer
The [Analyzer Package](Analyzer-Package) contains routines to analyze input and output data, convert units, and to develop data compliant with model resolution requirements, e.g., fuel and wind power curves based on simpler inputs. 

## Optimizer

## UserInterface 
The [UserInterface Package](UserInterface-Package) package contains a pyqt based arrangements of wizards, windows and input fields to create xml inputs for models, import data, create model input netcdf files and display results of the data import and model simulation runs. It provides an interface to the controller package to manage data and start running analysis.

## Controller
The Controller manages project specific state data, calls upon the input handler to complete input tasks, initiates model operations and receives information and event calls from the user interface. 