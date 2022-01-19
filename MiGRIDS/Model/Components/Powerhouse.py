# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import itertools
import sys
import os
import csv
import numpy as np
from ast import literal_eval
from MiGRIDS.Model.Components.Generator import Generator
from MiGRIDS.Analyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve
from MiGRIDS.Model.Operational.loadControlModule import loadControlModule


class Powerhouse:
    # __init()__ Class constructor. Initiates the setup of the individual generators as per the initial input.
    # Inputs:
    # self - self reference, always required in constructor
    # genIDS - list of generator IDs, which should be integers
    # genP - list of generator real power levels for respective generators listed in genIDS
    # genQ - list of generator reactive power levels for respective generators listed in genIDS
    # genDescriptor - list of generator descriptor XML files for the respective generators listed in genIDS, this should
    #   be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
    def __init__(self, genIDS, genStates, timeStep, genDescriptor, genDispatchFile, genScheduleFile,
                 genDispatchInputsFile, genScheduleInputsFile):
        # check to make sure same length data coming in
        if not len(genIDS)==len(genStates):
            raise ValueError('The length genIDS, genP, genQ and genStates inputs to Powerhouse must be equal.')
        # ************Powerhouse variables**********************
        # general
        self.timeStep = timeStep
        # List of generators and their respective IDs
        self.generators = []
        self.genIDS = genIDS

        # total capacities
        self.genPMax = 0
        self.genQMax = 0

        # Generator dispatch object
        self.genDispatchType = 1  # generator dispatch to use, 1 for proportional
        self.outOfNormalBounds = []
        self.outOfBounds = []
        self.outOfEfficientBounds = []
        self.genMol = []
        self.genMel = []
        self.genUpperNormalLoading = []
        self.genUpperLimit = []
        self.genLowerLimit = []

        # Cumulative operational data
        # Actual loadings
        self.genP = []
        self.genQ = []
        # Total available gen power without new dispatch
        self.genPAvail = []
        self.genQAvail = []

        # the minimum power output based on MOL
        self.genMolAvail = []
        # the minimum efficient power output based on MEL
        self.genMelAvail = []
        # the fuel consumption
        self.genFuelCons = []


        ## initiate generator dispatch and its inputs.
        # import gen energy dispatch
        self.genDispatch = loadControlModule(genDispatchFile, genDispatchInputsFile, 'genDispatch')
        self.genSchedule = loadControlModule(genScheduleFile, genScheduleInputsFile, 'genSchedule')


        # Populate the list of generators with generator objects
        for idx, genID in enumerate(genIDS):
            # Initialize generators
            self.generators.append(Generator(genID, genStates[idx], timeStep, genDescriptor[idx]))

            # Initial value for genP, genQ, genPAvail and genQAvail can be handled while were in this loop
            self.genPMax = self.genPMax + self.generators[idx].genPMax
            #TODO commented out because tag not in descriptor xml
            #self.genQMax = self.genQMax + self.generators[idx].genQMax
            self.genP += [self.generators[idx].genP]
            #self.genQ += [self.generators[idx].genQ]
            self.genPAvail += [self.generators[idx].genPAvail]
            # TODO commented out because tag not in descriptor xml
            #self.genQAvail += [self.generators[idx].genQAvail]
            self.genMolAvail += [self.generators[idx].genMolAvail]
            self.genMelAvail += [self.generators[idx].genMelAvail]
            self.genFuelCons += [self.generators[idx].genFuelCons]
            self.outOfNormalBounds.append(self.generators[idx].outOfNormalBounds)
            self.outOfBounds.append(self.generators[idx].outOfBounds)
            self.outOfEfficientBounds.append(self.generators[idx].outOfEfficientBounds)
            self.genMol.append(self.generators[idx].genMol) # the MOLs of each generator
            self.genMel.append(self.generators[idx].genMel)
            self.genUpperNormalLoading.append(self.generators[idx].genUpperNormalLoading)  # the genUpperNormalLoading of each generator
            self.genUpperLimit.append(self.generators[idx].genUpperLimit) # the upper limit of each generator
            self.genLowerLimit.append(self.generators[idx].genLowerLimit) # the lower limit of each generator
        # Create a list of all possible generator combination ID, MOL, upper normal loading, upper limit and lower limit
        # these will be used to schedule the diesel generators
        self.combinationsID = range(2**len(self.genIDS)) # the IDs of the generator combinations
        self.genCombinationsID = [] # the gen IDs in each combination
        self.genCombinationsMOL = np.array([])
        self.genCombinationsMEL = np.array([])
        self.genCombinationsUpperNormalLoading = []
        self.genCombinationsUpperLimit = []
        self.genCombinationsLowerLimit = []
        self.genCombinationsMinRange = []
        self.genCombinationsMaxRange = []
        self.genCombinationsPMax = []
        self.genCombinationsFCurve = []
        self.genMaxDiesCapCharge = []
        for nGen in range(len(self.genIDS)+1): # for all possible numbers of generators
            for subset in itertools.combinations(self.genIDS, nGen): # get all possible combinations with that number
                self.genCombinationsID.append(subset) # list of lists of gen IDs
                # get the minimum normal loading (if all operating at their MOL)
                subsetMOLPU = 0
                subsetMELPU = 0
                subsetGenUpperNormalLoading = 0 # the normal upper loading
                subsetGenUpperLimit = 0
                subsetGenLowerLimit = 0
                subsetPMax = 0
                powerLevelsPU = [] # pu power levels in combined fuel curve for combination
                fuelConsumption = [] # fuel consumption for combined fuel curve
                for gen in subset: # for each generator in the combination
                    subsetPMax += self.generators[self.genIDS.index(gen)].genPMax
                    subsetMOLPU = max(subsetMOLPU,self.genMol[self.genIDS.index(gen)]/self.generators[self.genIDS.index(gen)].genPMax) # get the max pu MOL of the generators
                    subsetMELPU = max(subsetMELPU, self.genMel[self.genIDS.index(gen)] / self.generators[
                        self.genIDS.index(gen)].genPMax)
                    subsetGenUpperNormalLoading += self.genUpperNormalLoading[self.genIDS.index(gen)]
                    subsetGenUpperLimit += self.genUpperLimit[self.genIDS.index(gen)]
                    subsetGenLowerLimit += self.genLowerLimit[self.genIDS.index(gen)]

                self.genCombinationsMOL = np.append(self.genCombinationsMOL, subsetMOLPU*subsetPMax) # pu MOL * P max =  MOL
                self.genCombinationsMEL = np.append(self.genCombinationsMEL, subsetMELPU * subsetPMax)
                self.genCombinationsUpperNormalLoading.append(subsetGenUpperNormalLoading)
                self.genCombinationsUpperLimit.append(subsetGenUpperLimit)
                self.genCombinationsLowerLimit.append(subsetGenLowerLimit)
                self.genCombinationsPMax.append(subsetPMax)
                self.genCombinationsFCurve.append(self.combFuelCurves(subset)) # append fuel curve for this combination
                self.genMaxDiesCapCharge.append(self.combMaxDiesCapCharge(subset)) # append the max diesel cap charge values for this combination

        # Update the current combination online
        for idx, combID in enumerate(self.combinationsID): # for each combination
            # get the gen IDs of online generators
            onlineGens = [genIDS[idx] for idx, x in enumerate(genStates) if x == 2]
            # if the gen IDs of this combination equal the gen IDs that are currently online, then this is current online combination
            if sorted(self.genCombinationsID[idx]) == sorted(onlineGens):
                self.onlineCombinationID = combID

        # CREATE LOOKUP TABLES FOR GENDISPATCH
        # UPPER NORMAL LOADING
        # Setup a list of all possible 'loading' values
        # Max combination will be needed during lookups as default value to revert to if there is no list of available
        # combinations for a lookup key, i.e., if the load is greater than the max upper normal loading of any gen comb.
        self.genCombinationsUpperNormalLoadingMaxIdx = int(np.argmax(np.asarray(self.genCombinationsUpperNormalLoading)))
        # loading = list(range(0, int(max(self.genCombinationsUpperNormalLoading)+1)))
        loading = list(range(0, int(self.genPMax)))
        self.lkpGenCombinationsUpperNormalLoading = {}
        self.lkpMinFuelConsumption = {}
        self.lkpMinFuelConsumptionGenID = {}
        self.lkpMinMOLGenID = {}
        self.lkpUserDefinedGenSchedule = {}
        for load in loading:
            combList = np.array([], dtype=int)
            fuelList = np.array([], dtype=int)
            fuelCombList = np.array([], dtype=int)
            for idy, genComb in enumerate(self.genCombinationsUpperNormalLoading):
                if load <= genComb:
                    combList = np.append(combList, idy)
                    if load < len(self.genCombinationsFCurve[idy]):
                        fuelList = np.append(fuelList, self.genCombinationsFCurve[idy][load][-1])
                        fuelCombList = np.append(fuelCombList, idy)
            if len(combList) > 0:
                minMOLComb = np.asarray(combList[np.argsort(self.genCombinationsMOL[combList])][0])
            fuelList, fuelCombList = self.selectMinFuelOption(load, fuelList, fuelCombList)
            self.lkpGenCombinationsUpperNormalLoading[load] = combList
            self.lkpMinMOLGenID[load] = minMOLComb
            # fuelSort = np.argsort(fuelList)
            self.lkpMinFuelConsumption[load] = fuelList#[fuelSort]
            self.lkpMinFuelConsumptionGenID[load] = fuelCombList#[fuelSort]
        if getattr(self.genSchedule, 'userDefinedGenList', False):
            self.importUserDefinedSchedule(readDir=self.genSchedule.userDefinedGenListPath)
        self.exportGenSchedule(saveDir=os.path.split(genDescriptor[0])[0])
        self.calcGenCombinationRanges()
        # CALCULATE AND SAVE THE MAXIMUM GENERATOR START TIME
        # this is used in the generator scheduling.
        self.maxStartTime = 0
        for gen in self.generators:
            self.maxStartTime = max(self.maxStartTime, gen.genStartTime)




    # combine fuel curves for a combination of generators
    # self - self reference
    # generators - a list of generator objects in the combination
    # combPMax - the name plate capacity of the combination of generators
    def combFuelCurves(self, genIDs):
        # get the max power of the combination
        combPMax = 0 # initiate to zero
        combFuelPower = [0]
        combFuelConsumption = [0]
        for genID in genIDs:
            combPMax += int(self.generators[self.genIDS.index(genID)].genPMax) # add each generator max power

        combFuelConsumption = np.array([0.0]*combPMax) # initiate fuel consumption array
        combFuelPower = list(range(combPMax)) # list of the powers corresponding to fuel consumption

        # for each generator, resample the fuel curve to get the desired loading levels
        for genID in genIDs:
            powerStep = self.generators[self.genIDS.index(genID)].genPMax / combPMax # the required power step in the fuel curve to get 1 kW steps in combined fuel curve
            genFC = GenFuelCurve() # initiate fuel curve object
            genFC.fuelCurveDataPoints = self.generators[self.genIDS.index(genID)].genFuelCurve # populate with generator fuel curve points
            genFC.genOverloadPMax = self.generators[self.genIDS.index(genID)].genPMax # set the max power to the nameplate capacity
            genFC.cubicSplineCurveEstimator(powerStep) # calculate new fuel curve
            combFuelConsumption += np.array([y for x, y in genFC.fuelCurve]) # add the fuel consumption for each generator

        if len(combFuelPower) == 0:
            combFuelPower = [0]
            combFuelConsumption = [0]

        return list(zip(combFuelPower, list(combFuelConsumption))) # return list of tuples

    # combine max diesel cap charging of ESS for a combination of generators
    # self - self reference
    # genIDs - a list of generator objects in the combination
    # returns a list of tuples (Diesel Max Loading, EESS max state of charge)
    def combMaxDiesCapCharge(self, genIDs):
        # for each genID, take the average of maxDiesCapCharge and maxDiesCapChargeE
         for idx, genID in enumerate(genIDs):
             if idx == 0:
                 gmdcce, gmdcc = zip(*self.generators[self.genIDS.index(genID)].maxDiesCapCharge)
             else:
                 gmdcce0, gmdcc0 = zip(*self.generators[self.genIDS.index(genID)].maxDiesCapCharge)
                 gmdcc = list((np.array(gmdcc) + np.array(gmdcc0)) / 2)
                 gmdcce = list((np.array(gmdcce) + np.array(gmdcce0)) / 2)
         if len(genIDs) == 0: # for diesel-off scenario
             gmdcc = [0]
             gmdcce = [0]
         return list(zip(gmdcce, gmdcc))


    # genDispatch class method. Assigns a loading to each online generator and checks if they are inside operating bounds.
    # Inputs:
    # self - self reference
    # newGenP - new total generator real load
    # newGenQ - new total generator reactive load
    def runGenDispatch(self, newGenP, newGenQ):
        self.genDispatch.runDispatch(self, newGenP, newGenQ)
        # check operating bounds for each generator
        for idx in range(len(self.genIDS)):
            self.generators[idx].checkOperatingConditions()
            # check if out of bounds
            self.outOfNormalBounds[idx] = self.generators[idx].outOfNormalBounds
            self.outOfBounds[idx] = self.generators[idx].outOfBounds
            self.outOfEfficientBounds[idx] = self.generators[idx].outOfEfficientBounds
            # get available power and minimum loading from each
            self.genPAvail[idx] = self.generators[idx].genPAvail
            #self.genQAvail[idx] = self.generators[idx].genQAvail
            self.genMolAvail[idx] = self.generators[idx].genMolAvail
            self.genMelAvail[idx] = self.generators[idx].genMelAvail
            # get the fuel consumption
            self.genFuelCons[idx] = self.generators[idx].genFuelCons
            # get the spinning reserve being supplied by the generators
            #self.genSRC[idx] = self.generators[idx].genPAvail - self.generators[idx].genP

        # manage generators that are warming up. If have run for 2x start up time, shut them off.
        # TODO: remove hard coded 2x and place as value in descriptor file and Generator class
        for gen in self.generators:
            # get the time remaining to turn on each generator
            # if greater than 2 times the required start time, it was likely started but is no longer needed
            if gen.genStartTimeAct > gen.genStartTime * 2:
                if gen.genState == 1: # only switch off if not running online
                    gen.genState = 0


    # genSchedule class method. Brings another generator combination online
    # Inputs:
    # self - self reference
    # scheduledLoad - the load that the generators will be expected to supply, this is predicted based on previous loading
    # scheduledSRC -  the minimum spinning reserve that the generators will be expected to supply
    # schedWithFuelCons -  minimize fuel consumption in the scheduling of generators. If false, it will schedule the combination with the lowest MOL
    def runGenSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay,underSRC):
        self.genSchedule.runSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay,
                                     powerAvailToSwitch, powerAvailToStay,underSRC)

    # switch generators on and off
    def switchGenComb(self,GenSwOn, GenSwOff):
        # bring online
        for genID in GenSwOn:
            self.generators[self.genIDS.index(genID)].genState = 2 # switch online
        # turn off
        for genID in GenSwOff:
            self.generators[self.genIDS.index(genID)].genState = 0  # switch offline

            # switch generators on and off
    def startGenComb(self, GenSwOn):
        # start the gennerators
        for genID in GenSwOn:
            self.generators[self.genIDS.index(genID)].genState = 1  # running but offline

    def exportGenSchedule(self, saveDir, fileName='genSchedule.csv'):
        #saves the gen schedule ranges to be used as a csv
        
        lkpToExport = {}
        if getattr(self.genSchedule, 'userDefinedGenList', False):
            lkpToExport = self.lkpUserDefinedGenSchedule.copy()
        elif getattr(self.genSchedule, 'minimizeFuel', False):
            lkpToExport = self.lkpMinFuelConsumptionGenID.copy()     
        else:
            lkpToExport = self.lkpMinMOLGenID.copy()
            
        prevGenID = -1
        with open(os.path.join(saveDir, fileName), 'w', newline='') as fn:
            csvfile = csv.writer(fn)
            # iterate through power steps in fuel consumption dict
            for pwr, FCompList in sorted(self.lkpMinFuelConsumption.items()):
                if FCompList.size==0:
                    genID = self.genCombinationsUpperNormalLoadingMaxIdx
                else:
                    # minFuelIDX = np.argmin(FCompList)
                    genID = lkpToExport[pwr]#[minFuelIDX]
                # Check if 0 power or change in genID of minimum fuel usage
                if (not pwr) or (not np.equal(prevGenID, genID)):
                    # print('Gen Combo', genID, 'starts at', pwr, 'kW')
                    csvfile.writerow([self.genCombinationsID[genID], pwr])
                    prevGenID = genID
                
    def importUserDefinedSchedule(self, readDir, fileName='userDefinedGenSchedule.csv'):
        # reads file from readDir/fileName and converts data to lookup table dict
        if os.path.isdir(readDir) and fileName is not None:
            fullPath = os.path.join(readDir, fileName)
        elif os.path.isfile(readDir):
            fullPath = readDir
            
        genSetPoints = {}
        prevPower = 0
        prevGenID = 0
        with open(fullPath, 'r') as fn:
            csvfile = csv.DictReader(fn, fieldnames=['gens', 'pwr'])
            for row in csvfile:
                # read row in as string - interpret pwr as int and evaluate gens to tuple
                genSetPoints[int(row['pwr'])] = literal_eval(row['gens'])
            
                for lkpPower in range(prevPower, int(row['pwr'])):
                    self.lkpUserDefinedGenSchedule[lkpPower] = np.array(prevGenID)
                prevGenID = self.genCombinationsID.index(literal_eval(row['gens']))
                prevPower = int(row['pwr'])
        for lkpPower in range(prevPower, int(self.genPMax)):
            self.lkpUserDefinedGenSchedule[lkpPower] = np.array(prevGenID)
            
    def calcGenCombinationRanges(self):
        # Calculates the minimum and maximum setpoints of the operating range 
        # each gen combinations based specified schedule (MOL, minFuel, user)
        lkp = {}
        if getattr(self.genSchedule, 'userDefinedGenList', False):
            lkp = self.lkpUserDefinedGenSchedule.copy()
        elif getattr(self.genSchedule, 'minimizeFuelComb', False):
            lkp = self.lkpMinFuelConsumptionGenID.copy()     
        else:
            lkp = self.lkpMinMOLGenID.copy()
            
        for combo in self.combinationsID:
            pwrRange = [pwr for pwr, lkpCombo in lkp.items() if lkpCombo == combo]
            
            if len(pwrRange):
                self.genCombinationsMinRange.append(min(pwrRange))
                self.genCombinationsMaxRange.append(max(pwrRange))
            else:
                self.genCombinationsMinRange.append([])
                self.genCombinationsMaxRange.append([])
            
            
    def selectMinFuelOption(self, pwr, fuelList, fuelCombList, threshold=0.01):
        #returns fuel consumption and generator combination ID of combination that
        # least amount of fuel in fuel list. 
        # Selects the option of the previous load step if lowest option and 
        # previous option are within fractional threshold input
        
        # If starting with an empty list, return an empty list
        if not len(fuelList):
            return fuelList, fuelCombList
        
        
        indSort = np.argsort(fuelList)
        minFuel = min(fuelList)
        minFuelID = fuelCombList[indSort[0]]
        
        prevFuel = self.lkpMinFuelConsumption.get(pwr-1, 0)
        if pwr and abs(minFuel-prevFuel)/minFuel < threshold:
            minFuel = prevFuel
            minFuelID = self.lkpMinFuelConsumptionGenID.get(pwr-1, 0)
        
        return np.array(minFuel), np.array(minFuelID)