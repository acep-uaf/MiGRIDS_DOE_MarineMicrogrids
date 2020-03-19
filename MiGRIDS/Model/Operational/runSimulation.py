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

from MiGRIDS.Model.Operational.SystemOperationA import SystemOperationsA
from MiGRIDS.Model.Operational.SystemOperations import SystemOperations
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Analyzer.DataWriters.writeNCFile import writeNCFile
from MiGRIDS.Model.Exceptions.NoDirectoryException import NoDirectoryException
from MiGRIDS.Model.Exceptions.MissingInputFile import MissingInputFileException
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath

class Simulation:
    def __init__(self,projectSetDir, projectSetupXML):

        self.projectSetDir = projectSetDir
        self.projectSetupFile = projectSetupXML
        self.outputDataDir = None
        # get set number
        dir_path = os.path.basename(projectSetDir)
        self.setNum = re.findall(r'\d+', dir_path)[len(re.findall(r'\d+', dir_path)) - 1]
        self.projectName = os.path.basename(getFilePath('Project', set=projectSetDir))


    def runIndividualSimulation(self,runNum):
        def stitchLoopWrite(var, dim):
            stitched = SO.stitchVariable(var)
            print(len(stitched))
            print(type(stitched))
            for idx, c in enumerate(zip(*stitched)):  # for each object
                writeNCFile(dim, c, 1, 0, self.getStandardUnit(var),
                            self.ncOutFileName(str(SO.getId(var, idx)) + str(var.replace('List', ''))))
            stitched = None

        def stitchAndWrite(prefix):
            stitched = SO.stitchVariable(prefix)
            print(len(stitched))
            print(type(stitched))
            # scale is always 1, offset is always 0
            writeNCFile(SO.DM.realTime, stitched, 1, 0, self.getStandardUnit(prefix),
                        self.ncOutFileName(prefix.replace('wf', 'wtg')))
            stitched = None
            return


        # Go to run directory and run
        runDir = os.path.join(self.projectSetDir, 'Run' + str(runNum))
        runCompDir = os.path.join(runDir, 'Components')  # component directory for this run
        # output data dir
        self.outputDataDir = os.path.join(runDir, 'OutputData')
        if not os.path.exists(self.outputDataDir):  # if doesnt exist, create
            os.mkdir(self.outputDataDir)

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

        for cpt in self.componentNames:  # for each component
            # check if component is a generator
            if 'gen' in cpt.lower():
                genDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(self.setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]
                genIDs += [cpt[3:]]
                genStates += [2]
            elif 'ees' in cpt.lower():  # or if energy storage
                eesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(self.setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]
                eesIDs += [cpt[3:]]
                eesStates += [2]
                eesSRC += [0]
                eesSOC += [0]
            elif 'tes' in cpt.lower():  # or if energy storage
                tesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(self.setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]
                tesIDs += [cpt[3:]]
                tesT += [295]
                tesStates += [2]
            elif 'wtg' in cpt.lower():  # or if wind turbine
                wtgDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(self.setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]
                wtgIDs += [cpt[3:]]
                wtgStates += [2]
            elif 'load' in cpt.lower():  # or if wind turbine
                loadDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(self.setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]

        # initiate the system operations

        SO = SystemOperations(self.outputDataDir, timeStep=self.timeStep, runTimeSteps=self.runTimeSteps,
                              loadRealFiles=self.loadProfileFile, loadReactiveFiles=[],
                              predictLoadFile=self.predictLoadFile,
                              predictLoadInputsFile=self.predictLoadInputsFile,
                              loadDescriptor=loadDescriptors, predictWindFile=self.predictWindFile,
                              predictWindInputsFile=self.predictWindInputsFile,
                              getMinSrcFile=self.getMinSrcFile, getMinSrcInputFile=self.getMinSrcInputFile,
                              reDispatchFile=self.reDispatchFile, reDispatchInputsFile=self.reDispatchInputFile,
                              genIDs=genIDs, genStates=genStates, genDescriptors=genDescriptors,
                              genDispatchFile=self.genDispatchFile,
                              genScheduleFile=self.genScheduleFile, genDispatchInputsFile=self.genDispatchInputFile,
                              genScheduleInputsFile=self.genScheduleInputFile,
                              wtgIDs=wtgIDs, wtgStates=wtgStates, wtgDescriptors=wtgDescriptors,
                              windSpeedDir=self.timeSeriesDir,
                              wtgDispatchFile=self.wtgDispatchFile, wtgDispatchInputsFile=self.wtgDispatchInputFile,
                              eesIDs=eesIDs, eesStates=eesStates, eesSOCs=eesSOC, eesDescriptors=eesDescriptors,
                              eesDispatchFile=self.eesDispatchFile, eesDispatchInputsFile=self.eesDispatchInputFile,
                              tesIDs=tesIDs, tesTs=tesT, tesStates=tesStates, tesDescriptors=tesDescriptors,
                              tesDispatchFile=self.tesDispatchFile, tesDispatchInputsFile=self.tesDispatchInputFile)

        SO.runSimulation()


        toStitch = ['powerhouseP', 'powerhousePch', 'rePLimit', 'wfPAvail', 'wfPImport', 'wfPch',
                    'wfPTot', 'srcMin', 'eessDis', 'eessP', 'tesP', 'genPAvail', 'onlineCombinationID', 'underSrc',
                    'outOfNormalBounds', 'outOfEfficientBounds', 'wfSpilledWindFlag', 'futureLoadList',
                    'futureSrc']

        [stitchAndWrite(p) for p in toStitch]

        stitchLoopList = ['futureWindList', 'wtgP', 'wtgPAvail', 'eesPLoss', 'eessSoc', 'eessSrc', 'genRunTime',
                          'genStartTime', 'genFuelCons', 'genP']
        [stitchLoopWrite(SO.DM.realTime, v) for v in stitchLoopList]



    def ncOutFileName(self,prefix,runNum):
        filename = '{}Set{}Run{}.nc'.format(prefix,str(self.setNum),str(runNum))

        return os.path.join(self.outputDataDir,filename)

    def getStandardUnit(self,prefix):
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






    def PrepareSimulationInput(self):

        def getFile(inputfile):
            filePath = os.path.join(self.projectSetDir, 'Setup',
                                    self.projectName + 'Set' + str(self.setNum) + inputfile[
                                        0].upper() + inputfile[
                                                     1:] + 'Inputs.xml')
            if not os.path.exists(filePath):
                raise MissingInputFileException(inputfile)
            return filePath


        # extract the numerical part of the set folder name

        # timeseries directory
        self.timeSeriesDir = getFilePath('Processed', set=self.projectSetDir)
          # get the time step
        self.timeStep = readXmlTag(self.projectSetupFile, 'timeStep', 'value', returnDtype='int')[0]
        # get the time steps to run
        runTimeSteps = readXmlTag(self.projectSetupFile, 'runTimeSteps', 'value')
        if len(runTimeSteps) == 1:  # if only one value, take out of list. this prevents failures further down.
            runTimeSteps = runTimeSteps[0]
            if (not runTimeSteps == 'all') & (not 'None' in runTimeSteps):
                self.runTimeSteps = int(runTimeSteps)
            elif 'None' in runTimeSteps:  # TODO remove this conversion and make sure it doesn't effect model reading in data
                self.runTimeSteps = 'all'
        elif runTimeSteps[0] == runTimeSteps[1]:
            self.runTimeSteps = 'all'
        else:  # convert to int
            self.runTimeSteps = [int(x) for x in runTimeSteps] #TODO should be additional check for string date vs string int
        try:
            # get the load predicting function
            self.predictLoadFile = readXmlTag(self.projectSetupFile, 'loadPredict', 'value')[0]
            self.predictLoadInputsFile = getFile(self.predictLoadFile)

            # get the wind predicting function
            self.predictWindFile = readXmlTag(self.projectSetupFile, 'windPredict', 'value')[0]
            self.predictWindInputsFile = getFile(self.predictWindFile)

            # get the ees dispatch
            self.eesDispatchFile = readXmlTag(self.projectSetupFile, 'eesDispatch', 'value')[0]
            self.eesDispatchInputFile = getFile(self.eesDispatchFile)

            # get the tes dispatch
            self.tesDispatchFile = readXmlTag(self.projectSetupFile, 'tesDispatch', 'value')[0]
            self.tesDispatchInputFile = getFile(self.tesDispatchFile)

            # get the minimum required SRC calculation
            self.getMinSrcFile = readXmlTag(self.projectSetupFile, 'getMinSrc', 'value')[0]

            self.getMinSrcInputFile = getFile(self.getMinSrcFile)

            # get the components to run
            self.componentNames = readXmlTag(self.projectSetupFile, 'componentNames', 'value')

            # get the load profile to run
            loadProfileFile = readXmlTag(self.projectSetupFile, 'loadProfileFile', 'value')[0]
            self.loadProfileFile = os.path.join(self.timeSeriesDir, loadProfileFile)

            # get the RE dispatch
            self.reDispatchFile = readXmlTag(self.projectSetupFile, 'reDispatch', 'value')[0]

            self.reDispatchInputFile = getFile(self.reDispatchFile)

            # get the gen dispatch
            self.genDispatchFile = readXmlTag(self.projectSetupFile, 'genDispatch', 'value')[0]

            self.genDispatchInputFile = getFile(self.genDispatchFile)
            # get the gen schedule
            self.genScheduleFile = readXmlTag(self.projectSetupFile, 'genSchedule', 'value')[0]

            self.genScheduleInputFile = getFile(self.genScheduleFile)

            # get the wtg dispatch
            self.wtgDispatchFile = readXmlTag(self.projectSetupFile, 'wtgDispatch', 'value')[0]

            self.wtgDispatchInputFile = getFile(self.wtgDispatchFile)

        except MissingInputFileException as e:
            print(e)
            print('Cannot proceed without file')
        return





