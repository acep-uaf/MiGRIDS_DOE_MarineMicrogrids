# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import os
import pickle
import numpy as np
# from ThermalSystem import ThermalSystem
from MiGRIDS.Model.Components.Demand import Demand
# from SolarFarm import Solarfarm
from MiGRIDS.Model.Components.ElectricalEnergyStorageSystem import ElectricalEnergyStorageSystem
from MiGRIDS.Model.Components.ThermalEnergyStorageSystem import ThermalEnergyStorageSystem
from MiGRIDS.Model.Components.Powerhouse import Powerhouse
from MiGRIDS.Model.Components.Windfarm import Windfarm
from MiGRIDS.Model.Operational.loadControlModule import loadControlModule
import sys

# add controls and components directories to path
sys.path.append('../Controls')
sys.path.append('../Components')


class SystemOperations:
    # System Variables
    # Generation and dispatch resources
    # FUTUREFEATURE: add genDispatch, genSchedule and wtgDispatch
    def __init__(self, outputDataDir, timeStep = 1, runTimeSteps = 'all', loadRealFiles = [], loadReactiveFiles = [], predictLoadFile = 'loadPredict1', predictLoadInputsFile = 'loadPredictInputs1', loadDescriptor = [],
                 predictWindFile = 'windPredict0', predictWindInputsFile = 'windPredictInputs0', getMinSrcFile = 'getMinSrc0', getMinSrcInputFile = 'getMinSrc0Inputs', reDispatchFile = 'reDispatch0', reDispatchInputsFile = 'reDispatchInputs0',
                 genIDs = [], genStates = [], genDescriptors = [], genDispatchFile = [],
                 genScheduleFile = [], genDispatchInputsFile = [], genScheduleInputsFile = [],
                 wtgIDs = [], wtgStates = [], wtgDescriptors = [], windSpeedDir = [], wtgDispatchFile = [], wtgDispatchInputsFile = [],
                 eesIDs = [], eesStates = [], eesSOCs = [], eesDescriptors = [], eesDispatchFile = [], eesDispatchInputsFile = [],
                 tesIDs = [], tesStates = [], tesTs = [], tesDescriptors = [], tesDispatchFile = [], tesDispatchInputsFile = []):
        """
        Constructor used for intialization of all sytem components
        :param timeStep: the length of time steps the simulation is run at in seconds.
        :param runTimeSteps: the timesteps to run. This can be 'all', an interger that the simulation runs up till, a list
        of two values of the start and stop indecies, or a list of indecies of length greater than 2 to use directly.
        :param loadRealFiles: list of net cdf files that add up to the full real load
        :param loadReactiveFiles: list of net cdf files that add up to the full reactive load. This can be left empty.
        :param predictLoad: If a user defines their own load predicting function, it is the path and filename of the function used
        to predict short term (several hours) future load. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: predictLoad0. The class name in the file must be 'predictLoad'. Inputs to the class are
        the load profile up till the current time step and the date-time in epoch format.
        :param predictWind: If a user defines their own wind predicting function, it is the path and filename of the function used
        to predict short term (several hours) future wind power. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: predictWind0. The class name in the file must be 'predictWind'. Inputs to the class are
        the wind profile up till the current time step and the date-time in epoch format.
        :param loadReactive: the net cdf file with the reactive load time series
        :param genIDS: list of generator IDs, which should be integers
        :param genP: list of generator real power levels for respective generators listed in genIDS
        :param genQ: list of generator reactive power levels for respective generators listed in genIDS
        :param genDescriptor: list of generator descriptor XML files for the respective generators listed in genIDS, this should
        be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
        :param wtgIDS: list of wtg IDs, which should be integers
        :param wtgP: list of wtg real power levels for respective wtg listed in genIDS
        :param wtgQ: list of wtg reactive power levels for respective wtg listed in wtgIDS
        :param wtgStates: list of wind turbine operating states 0 - off, 1 - starting, 2 - online.
        :param wtgDescriptor: list of generator descriptor XML files for the respective generators listed in genIDS, this should
        be a string with a relative path and file name, e.g., /InputData/Components/wtg1Descriptor.xml
        :param eesIDS: list of integers for identification of Energy Storage units.
        :param eesSOC: list of initial state of charge.
        :param eesState: list of the initial operating state, 0 - off, 1 - starting, 2 - online.
        :param eesDescriptor: list of relative path and file name of eesDescriptor-files used to populate static information.
        :param eesDispatchFile: If a user defines their own dispatch, it is the path and filename of the dispatch class used
        to dispatch the energy storage units. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: eesDispatch0. The class name in the file must be 'eesDispatch'
        """

        # Path for temp files
        self.outputDataDir = outputDataDir

        # import the load predictor
        self.predictLoad = loadControlModule(predictLoadFile, predictLoadInputsFile, 'loadPredict')

        # import the wind predictor
        # split into path and filename
        self.predictWind = loadControlModule(predictWindFile, predictWindInputsFile, 'windPredict')

        # import min src calculator
        # import renewable energy dispatch
        self.getMinSrc = loadControlModule(getMinSrcFile, getMinSrcInputFile, 'getMinSrc')

        # import renewable energy dispatch
        self.reDispatch = loadControlModule(reDispatchFile, reDispatchInputsFile, 'reDispatch')

        # load the real load
        if len(loadRealFiles) != 0:
            self.DM = Demand(timeStep, loadRealFiles, loadDescriptor, loadReactiveFiles, runTimeSteps)
        else:
            ValueError('At least one real load time-series file is required.')

        # Length of the load variable determines pre-allocation length for all recorded time series
        self.lenRealLoad = len(self.DM.realLoad)

        # initiate generator power house
        # TODO: seperate genDispatch from power house, put as input
        if len(genIDs) != 0:
            self.PH = Powerhouse(genIDs, genStates, timeStep, genDescriptors, genDispatchFile, genScheduleFile,
                 genDispatchInputsFile, genScheduleInputsFile)
        # initiate wind farm
        if len(wtgIDs) != 0:
            self.WF = Windfarm(wtgIDs, windSpeedDir, wtgStates, timeStep, wtgDescriptors, self.lenRealLoad,
                               wtgDispatchFile, wtgDispatchInputsFile, runTimeSteps)
        # initiate electrical energy storage system
        if len(eesIDs) != 0:
            self.EESS = ElectricalEnergyStorageSystem(eesIDs, eesSOCs, eesStates, timeStep, eesDescriptors, eesDispatchFile, eesDispatchInputsFile, self.lenRealLoad)
        # initiate the thermal energy storage system
        if len(tesIDs) != 0:
            self.TESS = ThermalEnergyStorageSystem(tesIDs, tesTs, tesStates, timeStep, tesDescriptors, tesDispatchFile, tesDispatchInputsFile)


        # save local variables
        self.timeStep = timeStep

    def getComponentId(self,prefix,i):
        if 'wind' in prefix.lower():
            return 'wtg' + self.WF.wtgIDs[i]
        if 'wtg' in prefix.lower():
            return 'wtg' + self.WF.wtgIDs[i]
        if 'ees' in prefix.lower():
            return 'ees' + self.EESS.eesIDs[i]
        if 'tes' in prefix.lower():
            return 'tes' + self.TESS.tesIDs[i]
        if 'gen' in prefix.lower():
            return 'gen' + self.PowerHouse.genIDS[i]

    # TODO: Put in seperate input file
    def runSimulation(self):
        
        # Keep track of how many steps are remaining to know if further splits need to anticipated
        # Initially this is the  total number of steps requested to be run
        remainingSteps = self.lenRealLoad
        
        # Setup the maximum number of steps before simulations are split and restarted
        # FUTUREFEATURE: this should be configured via _init_ and/or Setup.xml in the future
        self.maxStepsBeforeBreak = 60*60*24*7*4  # 4 weeks

        # Calculate a helper to pre-allocate all the time-series containers
        if remainingSteps <= self.maxStepsBeforeBreak:
            resultLength = self.lenRealLoad
            self.splitSimDataFlag = False
        else:
            resultLength = self.maxStepsBeforeBreak
            remainingSteps = remainingSteps - resultLength
            self.splitSimDataFlag = True

        # Set up for tracking data packages that will be saved intermittently to manage memory load.
        self.idx = 0
        snippetIdx = 0
        self.snippetTotal = 0

        # Initialize data channels
        self.initDataChannels(resultLength)

        # Depending on whether the splitSimDataFlag is set, either execute the simulation without interruption or
        # execute with stops to dump data channels to disk to avoid overcrowding the memory. The former case simply
        # calls runSimMainLoop, the latter adds checks to see if it is time to dump data, and extends the index
        # management to keep track of dumped data files.
        if self.splitSimDataFlag:
            # Loop through the desired time steps.
            for self.masterIdx, self.P in enumerate(self.DM.realLoad):

                # DUMP TRACKED VARIABLES TO KEEP MEMORY LOAD MANAGABLE
                # 1) Check if self.masterIdx is multiple of self.maxStepsBeforeBreak
                # 2) If (1) is True, dump all time-series variables into a temp pickle
                # 3) Re-initialize all time-series variables as pre-allocated list with len == resultLength
                # 4) Adjust self.idx by n*resultLength, where n is the number of temp saves performed
                # 5) Upon completion, stitch together the temp pickles for final (this should be called 'per variable' by
                #   runSimulation.py, e.g., SO.stitchVar('varName') right before the respective ncWrite is called.)
                if (self.masterIdx % self.maxStepsBeforeBreak) == 0 and self.masterIdx != 0:
                    # Check for the right length to re-initialize with. Normally this will be resultLength as set outside
                    # the loop, except, potentially for the last run through.
                    remainingStepsCheck = remainingSteps - resultLength
                    if remainingStepsCheck < 0:
                        resultLength = remainingSteps
                    else:
                        remainingSteps = remainingStepsCheck
                    # dump time-series
                    self.dumpAllTSVars(snippetIdx, resultLength)

                    # reset self.idx and keep track of the data snippets being written to pickles
                    self.idx = 0
                    snippetIdx = snippetIdx + 1
                    self.snippetTotal = self.snippetTotal + 1

                # Run the main code of the loop that is not directly affected by dumping parts of the data channels every
                # so often.
                self.runSimMainLoop()

            # Capture the last block of pickles [use 1 for resultLength, as the re-initialized vars will not be used].
            self.dumpAllTSVars(snippetIdx, 1)
            self.snippetTotal = self.snippetTotal + 1
        else:
            # Loop through the desired time steps.
            for self.masterIdx, self.P in enumerate(self.DM.realLoad):
                # Run the main code of the loop that is not directly affected by dumping parts of the data channels every
                # so often.
                self.runSimMainLoop()



    def dumpVariable(self, var, varName, snippetIdx):
        '''
        Dumps specified variable to a pickle. Is called by dumpAllTSVars

        :param var:
        :return:
        '''

        fileName = varName + 'SnippetNo_' + str(snippetIdx) + '.pickle'
        pFile = open(os.path.join(self.outputDataDir, fileName), 'wb')
        pickle.dump(var, pFile, pickle.HIGHEST_PROTOCOL)
        pFile.close()

    def getAllTSVars(self):
        '''
        Returns a list of all timeseries variables.
        :return:
        '''

        tsvars = [self.__getattribute__(a) for a in dir(self) if isinstance(self.__getattribute__(a), TSVar)]

        return tsvars

    def dumpAllTSVars(self, snippetIdx, resultLength):
        '''Sequential code for dumping all long TS vars in the major for-loop in runSimulation when conditions as met.'''

        tsVars = self.getAllTSVars()
        [self.dumpVariable(t.var,t.name,snippetIdx) for t in tsVars]

        # Re-initialize
        self.initDataChannels(resultLength)

    def stitchVariable(self, varName):
        '''
        Stiches time-series together from set of pickles if pickles were created, otherwise, it serves back the

        :param varName: variable name to stitch
        :param snippetTotal: total number of snippets to look for
        :return:
        '''

        if self.splitSimDataFlag:
            #fileList = os.listdir()
            variable = [None]*len(self.DM.realLoad)

            firstIdx = 0
            for snippetIdx in range(0, self.snippetTotal):
                fileName = varName + 'SnippetNo_' + str(snippetIdx) + '.pickle'
                pFile = open(fileName, 'rb')
                subVar = pickle.load(pFile)
                lenSubVar = len(subVar)
                variable[firstIdx:firstIdx+lenSubVar] = subVar
                firstIdx = firstIdx + lenSubVar
                # Clean up
                pFile.close()
                os.remove(fileName)
        else:
            attr = getattr(self, varName)
            variable = attr.var

        return variable
    
    def initDataChannels(self, varLength):
        '''
        Initialized all data channels that are being tracked with a given length. This function is called by 
        runSimulation() and by dumpAllTSVars().
         
        :param varLength: [int] length for the data channels
        :return: 
        '''
        channels_with_varLength = ['wtgPImport','wfPImport','wfPch','wfPTot','srcMin','eessDis','eessP',
                                   'powerhousePch','powerhouseP','genPAvail','wfPAvail','wtgPAvail','rePLimit','tesP','wfPset']
        [setattr(self, c, TSVar([None],varLength,c)) for c in channels_with_varLength]

        #TS vars with lengths greater than varLength and holders other than [None]
        self.wtgP = TSVar([[None] * len(self.WF.windTurbines)],varLength,'wtgP')
        self.eesPLoss = TSVar([[None] * len(self.EESS.electricalEnergyStorageUnits)],varLength,'eesPLoss')
        self.genP = TSVar([[None] * len(self.PH.generators)],varLength,'genP')
        self.genFuelCons = TSVar([[None] * len(self.PH.generators)],varLength,'genFuelCons')
        self.eessSrc = TSVar([[None] * len(self.EESS.electricalEnergyStorageUnits)],varLength,'eessSrc')
        self.eessSoc = TSVar([[None] * len(self.EESS.electricalEnergyStorageUnits)],varLength,'eessSoc')

        # TS vars with lengths greater than varLength and holders [0]
        # record for trouble shooting purposes
        self.futureLoadList = TSVar([0],varLength,'futureLoadList')
        self.futureWindList = TSVar([[0] * len(self.WF.windTurbines)], varLength,'futureWindList')
        self.futureSrc = TSVar([0], varLength, 'futureSRC')
        self.underSrc = TSVar([0], varLength, 'underSRC')
        self.outOfNormalBounds =TSVar([0],varLength, 'outOfNormalBounds')
        self.outOfEfficientBounds = TSVar([0],varLength, 'outOfEfficeintBounds')
        self.wfSpilledWindFlag = TSVar([0],varLength,'wfSpilledWindFlag')
        self.genStartTime = TSVar([[None] * len(self.PH.generators)], varLength,'genStartTime')
        self.genRunTime = TSVar([[None] * len(self.PH.generators)],varLength,'getRunTime')
        self.onlineCombinationID = TSVar([None],varLength,'onlineCombinationID')

    def runSimMainLoop(self):
        '''
        The main loop in runSimulation.
        FUTUREFEATURE this should be broken up into logical parts, such as 'recordDataChannels', 'handelDispatching', etc.
        :return:
        '''

        # Little helpers
        sumPHgenPAvail = sum(self.PH.genPAvail)  # summation is used six times in code, do once

        # get available wind power
        # FUTUREFEATURE: do the same for solar etc.
        self.WF.getWtgPAvail(self.masterIdx)

        # dispatch the renewable energy
        self.reDispatch.reDispatch(self)

        # get the required spinning reserve. Start off with a simple estimate
        self.getMinSrc.getMinSrc(self)
        srcMin = [self.getMinSrc.minSrcToStay, self.getMinSrc.minSrcToSwitch]

        # discharge the eess to cover the difference between load and generation
        eessDis = min([max([self.P - self.reDispatch.wfPimport - sumPHgenPAvail, 0]), sum(self.EESS.eesPoutAvail)])

        # get the diesel power output, the difference between demand and supply
        phP = self.P - self.reDispatch.wfPimport - eessDis
        # find the remaining ability of the EESS to supply SRC not supplied by the diesel generators
        eessSrcRequested = max([srcMin[0] - sumPHgenPAvail + phP, 0])

        # find the increase in loading allowed to charge the diesel generator
        if sumPHgenPAvail == 0:
            phPch = 0
        else:
            # for each energy storage unit SOC, find the appropriate diesel charging power based on the scheduled power
            # get the charging rules for the generators
            # find the loading on the generators
            phLoadMax = 0
            for eesSOC in self.EESS.eesSOC:
                # find the SOC
                eesMaxSOC, genMaxLoad = zip(*self.PH.genMaxDiesCapCharge[self.PH.onlineCombinationID])
                # find the lowest max SOC the SOC of the ees is under
                idxSOC = np.where(np.array(eesMaxSOC) > eesSOC)[0]
                if len(idxSOC) == 0:
                    idxSOC = len(eesMaxSOC) - 1
                else:
                    idxSOC = idxSOC[0]
                # use the max loading of all the EES that the gens are allowed to go to
                phLoadMax = max(phLoadMax, genMaxLoad[idxSOC])
            phPch = max(phLoadMax - phP / sumPHgenPAvail, 0) * sumPHgenPAvail
            # only able to charge as much as is left over from being charged from wind power
            phPch = min(sum(self.EESS.eesPinAvail) - self.reDispatch.wfPch, phPch)

        # dispatch the eess
        self.EESS.runEesDispatch(eessDis - self.reDispatch.wfPch - phPch, 0, eessSrcRequested, self.masterIdx)
        # read what eess managed to do
        eessP = sum(self.EESS.eesP[:])
        # recalculate generator power required
        phP = self.P - self.reDispatch.wfPimport - max([eessP, 0]) + phPch

        # dispatch the generators
        self.PH.runGenDispatch(phP, 0)

        # record values
        if hasattr(self, 'TESS'):  # check if thermal energy storage in the simulation
            self.tesP.var[self.idx] = sum(self.TESS.tesP)  # thermal energy storage power
        else:
            self.tesP.var[self.idx] = 0
        self.rePLimit.var[self.idx] = self.reDispatch.rePLimit
        self.wfPAvail.var[self.idx] = sum(self.WF.wtgPAvail[:])  # wind farm p avail
        self.wtgPAvail.var[self.idx] = self.WF.wtgPAvail[:]  # list of wind turbines  p avail
        self.wfPImport.var[self.idx] = self.reDispatch.wfPimport  # removed append usind self.idx
        self.wtgP.var[self.idx] = self.WF.wtgP[:]  # removed append, use ind self.idx
        self.wfPch.var[self.idx] = self.reDispatch.wfPch  # removed append, use ind self.idx
        self.wfPTot.var[self.idx] = self.reDispatch.wfPch + self.reDispatch.wfPimport
        self.srcMin.var[self.idx] = srcMin[0]
        self.eessDis.var[self.idx] = eessDis
        self.eessP.var[self.idx] = eessP
        self.eesPLoss.var[self.idx] = self.EESS.eesPloss[:]
        self.powerhouseP.var[self.idx] = phP
        self.powerhousePch.var[self.idx] = phPch
        self.genP.var[self.idx] = self.PH.genP[:]  # .append(self.PH.genP[:])
        self.genPAvail.var[self.idx] = sumPHgenPAvail  # sum(self.PH.genPAvail)
        self.genFuelCons.var[self.idx] = self.PH.genFuelCons[:]
        self.eessSrc.var[self.idx] = self.EESS.eesSRC[:]  # .append(self.EESS.eesSRC[:])
        self.eessSoc.var[self.idx] = self.EESS.eesSOC[:]  # .append(self.EESS.eesSOC[:])
        self.onlineCombinationID.var[self.idx] = self.PH.onlineCombinationID
        # record for troubleshooting
        genStartTime = []
        genRunTime = []
        for gen in self.PH.generators:
            genStartTime.append(gen.genStartTimeAct)
            genRunTime.append(gen.genRunTimeAct)
        self.genStartTime.var[self.idx] = genStartTime[:]  # .append(genStartTime[:])
        self.genRunTime.var[self.idx] = genRunTime[:]  # .append(genRunTime[:])

        ## If conditions met, schedule units
        # check if out of bounds opperation
        if True in self.EESS.underSRC or True in self.EESS.outOfBoundsReal or True in self.PH.outOfNormalBounds or \
                True in self.PH.outOfEfficientBounds or True in self.WF.wtgSpilledWindFlag:
            # predict what load will be
            # the previous 24 hours. 24hr * 60min/hr * 60sec/min = 86400 sec.
            self.predictLoad.loadPredict(self)
            self.futureLoad = self.predictLoad.futureLoad

            # predict what the wind will be
            self.predictWind.windPredict(self)
            self.futureWind = self.predictWind.futureWind
            # Sum of futureWind is used three times, calc once here
            sumFutureWind = sum(self.futureWind)
            if sumFutureWind > self.futureLoad:  # if wind is greater than load, scale back to equal the load
                ratio = self.futureLoad / sumFutureWind
                self.futureWind = [x * ratio for x in self.futureWind]
                sumFutureWind = sum(self.futureWind)

            # TODO: add other RE

            # get the ability of the energy storage system to supply SRC
            # first, calculate how much capacity should be reserved. This assumes that the eess will continue to discharge
            # at the current rate while warming up the diesel generators. This will avoid SRC being scheduled from the
            # eess which will not be available by the time the diesel generator is brought online.
            kWsReserved = max(eessDis * self.PH.maxStartTime, 0)
            eesSrcAvailMax = [None] * len(self.EESS.electricalEnergyStorageUnits)  # the amount of SRC available from all ees units
            # iterate through all ees and add their available SRC
            for idy, ees in enumerate(self.EESS.electricalEnergyStorageUnits):
                # assume the current discharge
                eesSrcAvailMax[idy] = ees.findPdisAvail(ees.eesSrcTime, 0, kWsReserved)

            # find the required capacity of the diesel generators
            # how much SRC can EESS cover? This can be subtracted from the load that the diesel generators must be
            # able to supply
            self.getMinSrc.getMinSrc(self, calcFuture=True)
            futureSRC = [self.getMinSrc.minSrcToStay, self.getMinSrc.minSrcToSwitch]
            # check if available SRC from EES is zero, to avoid dividing by zero
            # Helper sum variable, as sum(eesSrcAvailMax) is used up to six times
            sumEesSrcAvailMax = sum(eesSrcAvailMax)
            if sumEesSrcAvailMax > 0:
                coveredSRCStay = min([sumEesSrcAvailMax, futureSRC[0]])
                coveredSRCSwitch = min([sumEesSrcAvailMax, futureSRC[1]])
                # get the amount of SRC provided by each ees
                eesSrcScheduledStay = np.array(eesSrcAvailMax) * coveredSRCStay / sumEesSrcAvailMax
                eesSrcScheduledSwitch = np.array(eesSrcAvailMax) * coveredSRCSwitch / sumEesSrcAvailMax
            else:
                coveredSRCStay = 0
                coveredSRCSwitch = 0
                eesSrcScheduledStay = [0] * len(eesSrcAvailMax)
                eesSrcScheduledSwitch = [0] * len(eesSrcAvailMax)

            # get the ability of the energy storage system to supply the load by discharging, on top of the RE it is
            # covering with SRC
            eesSchedDischAvail = 0  # the amount of discharge available from all ees units for specified amount of time
            # iterate through all ees and add their available discharge
            #for index, ees in enumerate(self.EESS.electricalEnergyStorageUnits):
                # if generators running online, only schedule the ESS to be able to discharge if over the min SOC
                # the problem is that this will not
                # if ees.eesSOC > ees.eesDispatchMinSoc:
                #     # find the loss associated with the spinning reserve
                #     eesLoss = ees.findLoss(eesSrcScheduledSwitch[index], ees.eesSrcTime)
                #     # calculate the available discharge, taking into account the amount reserved to supply SRC and the
                #     # energy capacity required taking into account losses
                #     eesSchedDischAvail += ees.findPdisAvail(ees.eesDispatchTime, eesSrcScheduledSwitch[index],
                #                                             eesLoss + ees.eesSrcTime * eesSrcScheduledSwitch[index])

            # schedule the generators accordingly
            self.PH.runGenSchedule(self.futureLoad, sumFutureWind, futureSRC[1] - coveredSRCSwitch,
                                futureSRC[0] - coveredSRCStay,
                                eesSchedDischAvail, sumEesSrcAvailMax - sum(eesSrcScheduledStay),
                                any(self.EESS.underSRC))
            # TODO: incorporate energy storage capabilities and wind power into diesel schedule. First predict
            # the future amount of wind power. find available SRC from EESS. Accept the amount of predicted wind
            # power that can be covered by ESS (likely some scaling needed to avoid switching too much)

            # record for trouble shooting purposes
            if True in self.WF.wtgSpilledWindFlag:
                self.wfSpilledWindFlag.var[self.idx] = 1
            self.futureLoadList.var[self.idx] = self.futureLoad
            self.futureWindList.var[self.idx] = self.futureWind
            self.futureSrc.var[self.idx] = futureSRC[0]
            if True in self.EESS.underSRC:
                self.underSrc.var[self.idx] = 1
            if True in self.PH.outOfNormalBounds:
                self.outOfNormalBounds.var[self.idx] = 1
            if True in self.PH.outOfEfficientBounds:
                self.outOfEfficientBounds.var[self.idx] = 1

        # Last step in the regular for-loop [this is reset if the data is being saved - see below]
        self.idx = self.idx + 1

    def getId(self,var,idx):
        '''gets the id to use in writing a TSVar netcdf file
        :param: var is a string name of the file to write
        :idx is a integer index assocaited with the simulation count'''
        if var == 'gen':
            return self.PH.genIDS[idx]
        elif (var== 'ees') | (var == 'eess'):
            return self.EESS.eesIDs[idx]
        elif var == 'wtg':
            return self.WF.wtgIDS[idx]
        elif var == 'futureWind':
            return self.WF.wtgIDS[idx]

class TSVar:
    '''
    Class for holding timeseries variables and the name of the variable
    self.var =
    '''

    def __init__(self,spaceHolder,varLength,name):
        self.var = spaceHolder * varLength
        self.name = name