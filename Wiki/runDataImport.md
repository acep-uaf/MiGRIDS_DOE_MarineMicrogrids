 runDataImport.py

The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard netcdf format

This is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py). Or a project folder, with setup.xml and component descriptor xmls have been filled in manually. 

This script runs through the following 4 steps to get your data ready for the Model package.

  - Read data files into a single dataframe
  - Fix missing and bad data within the dataframe
  - standardize the timestep within the dataframe to the desired timestep to use in MiGRIDS. Default is 1 second.
  - Generate netCDFs

# Read data files
The input handler can read csv files as well as standard MET files. The file type is specified in the setup.xml under the tag 'fileFormat'. By calling [mergeInputs]()

Specify the location of the setup.xml.
```sh
fileName = os.path.join(*['YOUR PROJECT DIRECTORY','InputData','Setup','SampleProjectSetup.xml'])
```
Create a dictionary of of input values read from the setup.xml.
```sh
inputDictionary = readSetupFile(fileName)
```
### Import the data files.
[mergeInputs](InputHandler-Data-Import) combines files from each input folder. 
 Files of the specified format in setup.xml 'fileFormat' and specified 'fileLocation' are read into a single dataframe with the specified column names. Column names are created by cancatonating component name with its attribute.

```sh
df, listOfComponents = mergeInputs(inputDictionary)
```

df is a pandas.DataFrame object with columns representing each component and a datetime index. listOfComponents is a list of Component objects. Each Component contains attributes read from the component descriptor files. 

You can review the imported raw data by plotting it (matplotlib) and using looking at data metrics.

```sh
import matplotlib as plt
plt.plot(df[COMPONENTNAME])
df.describe()
```

If you need to correct any data that was imported you can fix it in your raw data files or correct it in the dataframe. Inspecting the import closely for bad or missing data will make subsequent steps more reliable.

If you are happy with the resulting dataframe, save it for future use:
```sh
os.chdir(inputDictionary['setupDir'])
out = open("df_raw.pkl","wb")
pickle.dump(df,out )
out.close()
out = open("component.pkl","wb")
pickle.dump(listOfComponents,out)
out.close()
```

To reload:
```sh
os.chdir(inputDictionary['setupDir'])
inFile = open("df_raw.pkl", "rb")
df= pickle.load(inFile)
inFile.close()
inFile = open("component.pkl", "rb")
listOfComponents = pickle.load(inFile)
inFile.close()
```

# Fix missing or bad data
Bad or missing data can occur when sensors go offline or incorrectly record data.
[fixBadData](InputHandler-Fix-Data) attempts to identify these time periods and replace the records with good data from elsewhere in the dataframe.
- The runTimeSteps argument can be used to truncate the dataframe to a range of target dates to model. Replacement data is drawn from the entire dataframe before it gets truncated.

```sh
df_fixed = fixBadData(df, inputDictionary['setupDir'],listOfComponents,inputDictionary['runTimeSteps'])
```
df\_fixed is a DataClass object that consists of raw and fixed dataframes. df\_fixed.fixed is a list of fixed dataframes. If the original dataset did not have any large data gaps the list will contain only 1 dataframe.
You can plot and review the dataset at this stage, and replace any sections of data that were not replaced correctly by editting df\_fixed directly.
* the code below would replace all wtg1P values between March 1 and March 2 with 300 in the first dataframe of fixed data.
  ```sh
   plt.plot(df_fixed.fixed[0]['wtg1P'])
   df_fixed.fixed[0].loc[pd.to_datetime('2007/03/01'):pd.to_datetime('2007/03/02'),'wtg1P'] = 300
    ```
# Fix timestep intervals
[fixDataInterval]() standardizes the data timestep between records.
If the timestep in the raw data is at a higher resolution that the desired modeling timestep data will be downsampled through taking a mean value. If the timestep of raw data is at a lower resolution it will be upsampled using the Langevin estimator to fill in new values. 
```sh
df_fixed_interval = fixDataInterval(df_fixed,inputDictionary['outputInterval'])
```
The resulting DataClass object can be used to generate input netcdf files for MiGRIDS Model package.
## Save the data object
Save the resulting DataClass object in case you need it later.
```sh
pickle.dump(df_fixed_interval, open("df_fixed_interval.p","wb"))
```

# Generate netCDFs.
Model package requires data inputs as netcdf files.

[dataframe2netcdf](InputHandler-netcdf) requires component information in the form of a dictionary
```sh
d = {}
for c in listOfComponents:
    d[c.column_name] = c.toDictionary()
```
Create the netcdf's.
```sh
dataframe2netcdf(df_fixed_interval.fixed, d)
```
netcdf files for each component will be generated in the [YOUR PROJECT]/InputData/TimeSeriesData/Processed
