
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
#         Nathan Green, njgreen3@alaska.edu, Alaska Center for Energy and Power
# Date: October 18, 2021
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

from MiGRIDS.Model.Operational.getIntListIndex import getIntListIndex


class genSchedule:
    def __init__(self,args):
        # whether to try to minimize fuel consumption or maximize RE contribution (by minimizing MOL of generators)
        self.minimizeFuel = args['minimizeFuel']
        self.userDefinedGenList = args['userDefinedGenList']
        self.userDefinedGenListPath = args['userDefinedGenListPath']
        self.switchGenDelay = args['switchGenDelay'] # how long, in seconds, to wait before switching gen combinations in non out of bounds operation
        self.switchGenTimer = 0

    def runSchedule(self, ph, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay, underSRC):
        # scheduled load is the difference between load and RE, the min of what needs to be provided by gen or ess
        scheduledLoad = max(futureLoad - futureRE,0)

        ## first find the generator capacity required
        capReqSwitch = max(int(scheduledLoad - powerAvailToSwitch + scheduledSRCSwitch),0)
        capReqStay = max(int(scheduledLoad - powerAvailToStay + scheduledSRCStay), 0)

        ## find desired generation combination, based on input preferences
        if self.userDefinedGenList:
            # single generator combination ID in a list (user defined)
            indSortSwitch = ph.lkpUserDefinedGenSchedule.get(capReqSwitch, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))
            indSortStay = ph.lkpUserDefinedGenSchedule.get(capReqStay, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))
                        
        elif self.minimizeFuel:
            # get the fuel consumption of possible gen combos at current capReq
            # order gen combos by fuel consumption rate
            indSortSwitch = ph.lkpMinFuelConsumptionGenID.get(capReqSwitch, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))
            indSortStay = ph.lkpMinFuelConsumptionGenID.get(capReqStay, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))

        else:
            # get the MOL of possible gen combos at current capReq
            # order gend combos by MOL
            indSortSwitch = ph.lkpGenCombinationsUpperNormalLoading.get(capReqSwitch, ph.genCombinationsUpperNormalLoadingMaxIdx)
            indSortStay = ph.lkpGenCombinationsUpperNormalLoading.get(capReqStay, ph.genCombinationsUpperNormalLoadingMaxIdx)
            
                    ## if the correct generator combination is online, do nothing. Otherwise, increment the timer
        if ph.onlineCombinationID == ph.combinationsID[indSortSwitch] or \
                ph.onlineCombinationID == ph.combinationsID[indSortStay]:
            self.switchGenTimer = 0 # reset the timer
        else:
            self.switchGenTimer = self.switchGenTimer + 1 #increment timer

        ## if gen switch timer is up, or out of bounds operation, then initiate gen switch
        if self.switchGenTimer >= self.switchGenDelay or True in ph.outOfNormalBounds or underSRC:
            # check how long it will take to switch online
            lenGenerators = len(ph.generators)
            turnOnTime = [None] * lenGenerators
            turnOffTime = [None] * lenGenerators
            for idx, gen in enumerate(ph.generators):
                # get the time remaining to turn on each generator
                # include this time step in the calculation. this avoids having to wait 1 time step longer than necessary to bring a diesel generator online.
                turnOnTime[idx] = gen.genStartTime - gen.genStartTimeAct - ph.timeStep
                # get the time remaining to turn off each generator
                turnOffTime[idx] = gen.genRunTimeMin - gen.genRunTimeAct - ph.timeStep

            # inititiate the generators to be switched on for this combination to all generators in the combination
            genSwOn = list(ph.genCombinationsID[indSortSwitch])
            # initiate the generators to be switched off for this combination to all generators currently online
            genSwOff = list(ph.genCombinationsID[ph.combinationsID.index(ph.onlineCombinationID)])
            # find common elements between switch on and switch off lists
            commonGen = list(set(genSwOff).intersection(genSwOn))
            # remove common generators from both lists
            for genID in commonGen:
                genSwOn.remove(genID)
                genSwOff.remove(genID)
            # for each gen to be switched get time, max time for combination is time will take to bring online

            # find max time to switch generators online
            onTime = 0
            for genID in genSwOn: # for each to be brought online in the current combination
                onTime = max(onTime,turnOnTime[ph.genIDS.index(genID)]) # max turn on time
            # find max of turn on time and turn off time
            SwitchTime = onTime # initiate to max turn on time
            for genID in genSwOff: # for each generator to be switched off in the current combination
                SwitchTime = max(SwitchTime, turnOffTime[ph.genIDS.index(genID)]) # check if there is a higher turn off time
            timeToSwitch = SwitchTime

            # if the most efficient can be switched on now, switch to it
            if timeToSwitch <= 0:
                # update online generator combination
                ph.onlineCombinationID = ph.combinationsID[indSortSwitch]
                ph.switchGenComb(genSwOn, genSwOff)  # switch generators
                for idx in range(len(ph.genIDS)):
                    # update genPAvail
                    ph.generators[idx].updateGenPAvail()
            # otherwise, start or continue warming up generators for most efficient combination
            else:
                ph.startGenComb(genSwOn)
