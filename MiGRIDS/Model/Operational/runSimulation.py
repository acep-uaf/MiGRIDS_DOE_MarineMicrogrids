# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 28, 2018
# License: MIT License (see LICENSE file of this package for more information)

#here = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(here,".."))
import glob
import sqlite3
import time
# add to sys path

import re
import os
from MiGRIDS.Model.Operational.SystemOperations import SystemOperations
from MiGRIDS.Controller.UIHandler import UIHandler
#from MiGRIDS.Controller.RunHandler import RunHandler


#here = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(here, '../'))
#sys.path.append(here)
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Analyzer.DataWriters.writeNCFile import writeNCFile
from MiGRIDS.Model.Exceptions.NoDirectoryException import NoDirectoryException
from MiGRIDS.Model.Exceptions.MissingInputFile import MissingInputFileException
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath

def runSimulation(projectSetDir = ''):
    controller = RunHandler()
    #TODO update progress bar here to 1
    if projectSetDir == '':
       #throw an error
       raise NoDirectoryException("Specify a valid directory")

    def getFile(inputfile):
       filePath = os.path.join(projectSetDir, 'Setup',
                               projectName + 'Set' + str(setNum) + inputfile[
                                   0].upper() + inputfile[
                                                1:] + 'Inputs.xml')
       if not os.path.exists(filePath):
           raise MissingInputFileException(inputfile)
       return filePath

       # get set number
    dir_path = os.path.basename(projectSetDir)
    #extract the numerical part of the set folder name
    setNum = re.findall(r'\d+', dir_path)[len(re.findall(r'\d+', dir_path)) -1]

    #setNum = str(dir_path[3:])
    # get the project name
    #os.chdir(projectSetDir)
    #os.chdir('../..')
    #projectDir = os.getcwd()
    projectName = os.path.basename(getFilePath('Project',set=projectSetDir))

    # timeseries directory
    timeSeriesDir = getFilePath('Processed',set=projectSetDir)

    # get the set setup file
    projectSetupFile = os.path.join(projectSetDir,'Setup',projectName+'Set'+str(setNum)+'Setup.xml')

    # get the time step
    timeStep = readXmlTag(projectSetupFile,'timeStep','value',returnDtype = 'int')[0]

    # get the time steps to run
    runTimeSteps = readXmlTag(projectSetupFile,'runTimeSteps','value')

    if len(runTimeSteps) == 1: # if only one value, take out of list. this prevents failures further down.
        runTimeSteps = runTimeSteps[0]
        if (not runTimeSteps == 'all') & (not 'None' in runTimeSteps):
            runTimeSteps = int(runTimeSteps)
        elif 'None' in runTimeSteps: #TODO remove this conversion and make sure it doesn't effect model reading in data
            runTimeSteps = 'all'

    else: # convert to int
        runTimeSteps = [int(x) for x in runTimeSteps]
    try:
        # get the load predicting function
        predictLoadFile = readXmlTag(projectSetupFile,'loadPredict','value')[0]
        predictLoadInputsFile = getFile(predictLoadFile)

        # get the wind predicting function
        predictWindFile = readXmlTag(projectSetupFile,'windPredict','value')[0]
        predictWindInputsFile = getFile(predictWindFile)

        # get the ees dispatch
        eesDispatchFile = readXmlTag(projectSetupFile,'eesDispatch','value')[0]
        eesDispatchInputFile = getFile(eesDispatchFile)

        # get the tes dispatch
        tesDispatchFile = readXmlTag(projectSetupFile, 'tesDispatch', 'value')[0]
        tesDispatchInputFile = getFile(tesDispatchFile)

        # get the minimum required SRC calculation
        getMinSrcFile = readXmlTag(projectSetupFile, 'getMinSrc', 'value')[0]

        getMinSrcInputFile = getFile(getMinSrcFile)

        # get the components to run
        componentNames = readXmlTag(projectSetupFile, 'componentNames', 'value')

        # get the load profile to run
        loadProfileFile = readXmlTag(projectSetupFile, 'loadProfileFile', 'value')[0]
        loadProfileFile = os.path.join(timeSeriesDir,loadProfileFile)

        # get the RE dispatch
        reDispatchFile = readXmlTag(projectSetupFile, 'reDispatch', 'value')[0]

        reDispatchInputFile = getFile(reDispatchFile)

        # get the gen dispatch
        genDispatchFile = readXmlTag(projectSetupFile, 'genDispatch', 'value')[0]

        genDispatchInputFile = getFile(genDispatchFile)
        # get the gen schedule
        genScheduleFile = readXmlTag(projectSetupFile, 'genSchedule', 'value')[0]

        genScheduleInputFile = getFile(genScheduleFile)

        # get the wtg dispatch
        wtgDispatchFile = readXmlTag(projectSetupFile, 'wtgDispatch', 'value')[0]

        wtgDispatchInputFile = getFile(wtgDispatchFile)

    except MissingInputFileException as e:
        print(e)
        print('Cannot proceed without file')

    searchpath = os.path.join(*[projectSetDir,  'Run*'])
    runCount = len(glob.glob(searchpath))
    controller.sender.notifyProgress(2,'Simulation')
    while 1:
        # read the SQL table of runs in this set and look for the next run that has not been started yet.
        #conn = sqlite3.connect(os.path.join(projectSetDir,'set' + str(setNum) + 'ComponentAttributes.db') )# create sql database
        #df = pd.read_sql_query('select * from compAttributes',conn)
        # try to find the first 0 value in started column

        runNum = controller.getNextRun('Set' + setNum)
        if runNum == None:
            break
        #try:
        #   runNum = list(df['started']).index(0)
        #except: # there are no more simulations left to run
            #break
        # set started value to 1 to indicate starting the simulations
        #df.at[runNum, 'started'] = 1

        controller.updateRunToStarted('Set'+str(setNum),runNum)
        #df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        #conn.close()
        # Go to run directory and run
        runDir = os.path.join(projectSetDir,'Run'+ str(runNum))
        runCompDir = os.path.join(runDir,'Components') # component directory for this run
        # output data dir
        outputDataDir = os.path.join(runDir, 'OutputData')
        if not os.path.exists(outputDataDir): # if doesnt exist, create
            os.mkdir(outputDataDir)

        eesIDs = []
        eesSOC = []
        eesStates = []
        eesSRC = []
        eesDescriptors = []
        tesIDs = []
        tesT = []
        tesStates = []
        tesDescriptors = []
        wtgIDs = []
        wtgStates = []
        wtgDescriptors = []
        genIDs = []
        genStates = []
        genDescriptors = []
        loadDescriptors = []


        for cpt in componentNames:  # for each component
            # check if component is a generator
            if 'gen' in cpt.lower():
                genDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                genIDs += [cpt[3:]]
                genStates += [2]
            elif 'ees' in cpt.lower():  # or if energy storage
                eesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                eesIDs += [cpt[3:]]
                eesStates += [2]
                eesSRC += [0]
                eesSOC += [0]
            elif 'tes' in cpt.lower():  # or if energy storage
                tesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                tesIDs += [cpt[3:]]
                tesT += [295]
                tesStates += [2]
            elif 'wtg' in cpt.lower():  # or if wind turbine
                wtgDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                wtgIDs += [cpt[3:]]
                wtgStates += [2]
            elif 'load' in cpt.lower():  # or if wind turbine
                loadDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]

        # initiate the system operations
        # code profiler
        # pr0 = cProfile.Profile()
        # pr0.enable()
        SO = SystemOperations(outputDataDir, timeStep = timeStep, runTimeSteps = runTimeSteps, loadRealFiles = loadProfileFile, loadReactiveFiles = [],
                              predictLoadFile = predictLoadFile, predictLoadInputsFile=predictLoadInputsFile,
                              loadDescriptor = loadDescriptors, predictWindFile = predictWindFile, predictWindInputsFile=predictWindInputsFile,
                              getMinSrcFile = getMinSrcFile, getMinSrcInputFile = getMinSrcInputFile, reDispatchFile = reDispatchFile, reDispatchInputsFile = reDispatchInputFile,
                         genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatchFile = genDispatchFile,
                            genScheduleFile = genScheduleFile, genDispatchInputsFile= genDispatchInputFile, genScheduleInputsFile= genScheduleInputFile,
                         wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, windSpeedDir = timeSeriesDir,
                            wtgDispatchFile=wtgDispatchFile, wtgDispatchInputsFile=wtgDispatchInputFile,
                         eesIDs = eesIDs, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptors, eesDispatchFile = eesDispatchFile, eesDispatchInputsFile= eesDispatchInputFile,
                         tesIDs = tesIDs, tesTs = tesT, tesStates=tesStates, tesDescriptors=tesDescriptors, tesDispatchFile=tesDispatchFile, tesDispatchInputsFile = tesDispatchInputFile )
        # stop profiler
        # pr0.disable()
        #pr0.print_stats(sort="calls")

        # run the simulation
        # code profiler
        # pr1 = cProfile.Profile()
        # pr1.enable()
        # run sim
        SO.runSimulation()
        # stop profiler
        # pr1.disable()
        # pr1.print_stats(sort="calls")

        # save data
        #os.chdir(outputDataDir)

        start_file_write = time.time()
        def ncOutFileName(prefix):
            filename = '{}Set{}Run{}.nc'.format(prefix,str(setNum),str(runNum))

            return os.path.join(outputDataDir,filename)

        def getStandardUnit(prefix):
            #a prefix is formatted as nameAttribute
            attrList = re.findall('[A-Z][^A-Z]*', prefix)
            if (len(attrList) >1):
                attr = attrList[-2]
            else:
                attr = attrList[-1]
            #each attribute has a standard unit
            dir_path = os.path.dirname(os.path.realpath(__file__))
            unitConventionDir = os.path.join(dir_path, *['..','..', 'Analyzer', 'UnitConverters'])
            # get the default unit for the data type
            units = readXmlTag('internalUnitDefault.xml', ['unitDefaults', attr], 'units',
                       unitConventionDir)
            if units != None:
                return units[0]
            else:
                return 'NA'

        def stitchLoopWrite(var,dim):
            stitched = SO.stitchVariable(var)
            print(len(stitched))
            print(type(stitched))
            for idx, c in enumerate(zip(*stitched)):  # for each object
                writeNCFile(dim, c, 1, 0, getStandardUnit(var),
                             ncOutFileName(str(SO.getId(var,idx)) + str(var.replace('List',''))))
            stitched = None

        def stitchAndWrite(prefix):
            stitched = SO.stitchVariable(prefix)
            print(len(stitched))
            print(type(stitched))
            # scale is always 1, offset is always 0
            writeNCFile(SO.DM.realTime, stitched, 1, 0, getStandardUnit(prefix),
                        ncOutFileName(prefix.replace('wf', 'wtg')))
            stitched = None
            return



        toStitch = ['powerhouseP','powerhousePch','rePLimit','wfPAvail','wfPImport','wfPch',
                    'wfPTot','srcMin','eessDis','eessP','tesP','genPAvail','onlineCombinationID','underSrc',
                    'outOfNormalBounds','outOfEfficientBounds','wfSpilledWindFlag','futureLoadList',
                    'futureSrc']

        [stitchAndWrite(p) for p in toStitch]


        #future load list was named differently form the rest - why?
        # Stitch futureLoadList and write to disk
        #futureLoadList = SO.stitchVariable('futureLoadList')
        #writeNCFile(SO.DM.realTime, futureLoadList, 1, 0, 'kW',
          #          'futureLoad' + str(setNum) + 'Run' + str(runNum) + '.nc')  # future Load predicted
        #futureLoadList = None

        stitchLoopList=['futureWindList','wtgP','wtgPAvail','eesPLoss','eessSoc','eessSrc','genRunTime','genStartTime','genFuelCons','genP']
        [stitchLoopWrite(SO.DM.realTime,v) for v in stitchLoopList]
        #print('File write operation elapsed time: ' + str(time.time() - start_file_write))

        # # set the value in the 'finished' for this run to 1 to indicate it is finished.
        # conn = sqlite3.connect(
        #     os.path.join(projectSetDir, 'set' + str(setNum) + 'ComponentAttributes.db'))  # create sql database
        # df = pd.read_sql_query('select * from compAttributes', conn)
        # # set finished value to 1 to indicate this run is finshed
        # df.loc[runNum, 'finished'] = 1
        # df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        # conn.close()
        # TOOD update progress bar: while loop bar length is 8. Update by 8/num of runs

        controller.updateRunToFinished('Set' + setNum, runNum)

        controller.sender.notifyProgress(1/runCount, 'Simulation')


