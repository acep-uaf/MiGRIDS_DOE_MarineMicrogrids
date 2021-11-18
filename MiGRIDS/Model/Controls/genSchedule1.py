
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
        
    def runSchedule(self, ph, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay, underSRC):
        # scheduled load is the difference between load and RE, the min of what needs to be provided by gen or ess
        scheduledLoad = max(futureLoad - futureRE,0)

        ## first find all generator combinations that can supply the load within their operating bounds
        # find all with capacity over the load and the required SRC
        capReq = max(int(scheduledLoad - powerAvailToSwitch + scheduledSRCSwitch),0)

        ## then check how long it will take to switch to any of the combinations online
        lenGenerators = len(ph.generators)
        turnOnTime = [None]*lenGenerators
        turnOffTime = [None]*lenGenerators
        for idx, gen in enumerate(ph.generators):
            # get the time remaining to turn on each generator
            # include this time step in the calculation. this avoids having to wait 1 time step longer than necessary to bring a diesel generator online.
            turnOnTime[idx] = gen.genStartTime - gen.genStartTimeAct - ph.timeStep
            # get the time remaining to turn off each generator
            turnOffTime[idx] = gen.genRunTimeMin - gen.genRunTimeAct - ph.timeStep

        # find desired generation combination
        if self.userDefinedGenList:
            # single generator combination ID in a list (user defined)
            indSort = ph.lkpUserDefinedGenSchedule.get(capReq, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))
                        
        elif self.minimizeFuel:
            # get the ID of most efficient fuel consumption combination at current capReq
            # predetermined in powerhouse init
            indSort = ph.lkpMinFuelConsumptionGenID.get(capReq, np.array([ph.genCombinationsUpperNormalLoadingMaxIdx]))
        else:
            # get the MOL of possible gen combos at current capReq
            # order gend combos by MOL
            indCap = np.asarray(ph.lkpGenCombinationsUpperNormalLoading.get(capReq, ph.genCombinationsUpperNormalLoadingMaxIdx), dtype=int)
            # check if the current online combination is capable of supplying the projected load minus the power available to
            # help the current generator combination stay online
            if ph.onlineCombinationID not in indCap and not (True in ph.outOfNormalBounds) and not underSRC: # keep current generating combingation in the mix unless has gone out of bounds for allotted amount
                # do not add the current generating option if it is diesel-off and it does not have enough SRC
                indCap = np.append(indCap,ph.onlineCombinationID)
            indSort = indCap[np.argsort(ph.genCombinationsMOL[indCap])]
        
        # inititiate the generators to be switched on for this combination to all generators in the combination
        genSwOn = list(ph.genCombinationsID[indSort[0]])
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
        
        ## bring the best option that can be switched immediatley, if any
        # if the most efficient option can't be switched, start warming up generators
        
        # if the most efficient can be switched on now, switch to it
        if timeToSwitch <= 0:
            # update online generator combination
            ph.onlineCombinationID = ph.combinationsID[indSort[0]]
            ph.switchGenComb(genSwOn, genSwOff)  # switch generators
            for idx in range(len(ph.genIDS)):
                # update genPAvail
                ph.generators[idx].updateGenPAvail()
        # otherwise, start or continue warming up generators for most efficient combination
        else:
            ph.startGenComb(genSwOn)
            # otherwise, if a generator is out of bounds (not just normal bounds) switch to the best possible, if can
            # if (True in (np.array(timeToSwitch)<=0)) & (True in ph.outOfBounds):
            #     # find most efficient option that can be switched now
            #     indBest = next((x for x in range(len(indSort)) if timeToSwitch[indSort[x]] <= 0 )) # indBest wrt indSort
            #     # update online generator combination
            #     ph.onlineCombinationID = ph.combinationsID[indInBounds[indSort[indBest]]]
            #     ph.switchGenComb(genSwOn[indSort[indBest]],genSwOff[indSort[indBest]]) # switch generators
            #     for idx in range(len(ph.genIDS)):
            #         # update genPAvail
            #         ph.generators[idx].updateGenPAvail()