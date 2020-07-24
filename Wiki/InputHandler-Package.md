# Introduction
The input handler takes data files from the user, parses them according to input specifications and saves standard netCDF files with the data. The input data needs to be linked to component Descriptor files. An example of the process can be found in [runDataImport.py](runDataImport).

Figure 1 shows the general flow of the input handler. 

![Figure 1: Input Handler flow diagram. ](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/GBS%20InputHandler.png)

The InputHandler package consists of 5 main operations:

* A project needs to be initiated to establish the appropriate file structure through [initiateProject](InputHandler-initiateProject).

* Data gets loaded in its raw form depending on input formats specified [mergeInputs](InputHandler-Data-Import).

* Missing or bad data needs to get replaced with good data [fixBadData](InputHandler-Fix-Data). When possible data from another time period is used to replace bad data. If replacement data is not available new data is simulated.

* The records need to be either up sampled or down sampled to the desired time step used in the Model package [fixDataInterval](InputHandler-Fix-Date-Interval).

* Once the input dataframe is generated a netcdf file is required for each column of data [dataframe2netcdf](InputHandler-netcdf).


