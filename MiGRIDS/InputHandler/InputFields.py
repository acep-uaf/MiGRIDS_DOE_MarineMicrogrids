# Projet: MiGRIDS
# Created by: # Created on: 1/29/2020
# Purpose :  Specify constanstants used when reading and writing fileds for xml files InputFields

#SetupXML
FILENAME = "fileName.value"
FILEDIR = "inputFileDir.value" #a  directory containing raw input data
FILETYPE = "inputFileType.value" #the type of file containing raw input data
DATECHANNELFORMAT = "dateChannel.format" #the format of date values within a raw input file
DATECHANNEL="dateChannel.value" #The name of the field containing date values in a raw input file
TIMECHANNELFORMAT = "timeChannel.format" #the format of time values within a raw input file
TIMECHANNEL =  "timeChannel.value" #The name of the field containing time values within a raw input file
TIMEZONE = "timeZone.value" #the timezone associated with date/time values in a raw input file
FLEXIBLEYEAR = "flexibleYear.value"  #Whether or not years contained within a raw input file are flexible and month/day/time can be matched by ignoring year
INPUTTIMESTEP =  "inputtimeStep.value" #The approximate timestep of the raw input data
TIMESTEP = "timeStep.value" #the target timestep of processe
TIMESTEPUNIT = "timeStep.unit"
UTCOFFSET ="inputUTCOffset.value" #offset in hours of the raw datetime from UTC
UTCUNIT = "inputUTCOffset.unit"
DST = "inputDST.value" #wheter or not the input datetime uses daylight savings time
HEADERNAME = "headerName.value" #name of fields in raw input fales
COMPONENTATTRIBUTEUNIT =  "componentAttribute.unit" #unit assocaited with data values
COMPONENTATTRIBUTE = "componentAttribute.value" #The attribute associated with data
COMPONENTNAME = "componentName.value" #the individual component name associated with a field of data in an input file
COMPONENTNAMES = "componentNames.value" #the names of all component sin a file
RUNTIMESTEPS = "runTimeSteps.value" #the subset of records to run (subset on processed files not raw)


