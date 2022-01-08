# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)
import sys

from bs4 import BeautifulSoup as Soup

sys.path.append('../')
from MiGRIDS.Analyzer.CurveAssemblers.esLossMapAssembler import esLossMap
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
import numpy as np
from MiGRIDS.Model.Operational.getIntListIndex import getIntListIndex

class ElectricalEnergyStorage:
    '''
        Electrical Storage class: contains all necessary information for a single electrical storage unit. Multiple
        electrical storage units can be aggregated in an Electrical Storage System object (see
        ElectricalStorageSystem.py), which further is aggregated in the SystemOperations object (see
        SystemOperations.py).
        '''
    # Constructor
    def __init__(self, eesID, eesSOC, eesState, timestep, eesDescriptor, timeSeriesLength):
        """
        Constructor used for intialization of an Energy Storage unit in Energy Storage System class.
        :param eesID: integer for identification of object within Energy Storage System list of ees units.
        :param eesSOC: initial state of charge.
        :param eesState: the current operating state, 0 - off, 1 - starting, 2 - online.
        :param eesDescriptor: relative path and file name of eesDescriptor-file used to populate static information.
        """
        # manage run time timers
        self.eesRunTimeAct = 0
        self.eesRunTimeTot = 0
        self.eesStartTimeAct = 0

        # write initial values to internal variables
        self.eesID = eesID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.eesSOC = eesSOC # Current state of charge in pu
        self.eesState = eesState  # Generator operating state [dimensionless, index]. See docs for key.
        self.timeStep = timestep  # the time step used in the simulation in seconds


        # run the descriptor parser file to grab information from the descriptor file for this unit
        self.eesDescriptorParser(eesDescriptor)

        # this sets the amount of SRC that the ess needs to be able to provide and the calculates the minimum ees stored
        # energy that must be maintained. run self.setSRC to set the SRC.
        self.setSRC(0)

        # this updates the power availble from this ees to be used in scheduling generating units
        self.updatePScheduleMax()

        # these values will be set when checkOperatingConditions is run
        self.eesP = 0
        self.eesQ = 0
        self.eesPinAvail = 0
        self.eesPinAvail_1 = 0
        self.eesPsrcAvail = 0
        self.eesPsrcAvailMax = 0
        #TODO commented out because tag not in xml
        #self.eesQinAvail = self.eesQInMax
        self.eesPoutAvail = 0
        #TODO commented out because tag not in xml
        #self.eesQoutAvail = self.eesQOutMax
        self.underSRC = 0
        self.prevUnderSrc = [0]*timeSeriesLength
        self.outOfBoundsReal = 0
        self.outOfBoundsReactive = 0
        self.eesPoutAvailOverSrc = 0
        self.eesPoutAvailOverSrc_1 = 0
        self.eesPloss = 0
        self.checkOperatingConditions(0)

    # energy storage descriptor parser
    def eesDescriptorParser(self, eesDescriptor):
        """
        Reads the data from a given eesDescriptor file and uses the information given to populate the
        respective internal variables.

        :param eesDescriptor: relative path and file name of eesDescriptor.xml-file that is used to populate static
        information

        :return:
        """
        # read xml file
        eesDescriptorFile = open(eesDescriptor, "r")
        eesDescriptorXml = eesDescriptorFile.read()
        eesDescriptorFile.close()
        eesSoup = Soup(eesDescriptorXml, "xml")

        # Dig through the tree for the required data
        self.eesName = eesSoup.component.get('name')
        self.eesPOutMax = float(eesSoup.POutMaxPa.get('value'))  # max discharging power
        self.eesPInMax = float(eesSoup.PInMaxPa.get('value'))  # max charging power
        #TODO commented out because does not exist in xml
        #self.eesQOutMax = float(eesSoup.QOutMaxPa.get('value'))  # max discharging power reactive
        #self.eesQInMax = float(eesSoup.QInMaxPa.get('value'))  # max charging power reactive
        # FUTUREFEATURE: add the effect of charge/discharge rate on capacity. Possibly add something similar to the LossMap
        self.eesEMax = float(eesSoup.ratedDuration.get('value'))*self.eesPOutMax # the maximum energy capacity of the EES in kWs
        # check if EMax is zero, this is likely because it is a zero EES condition. Set it to 1 kWs in order not to crash the
        # SOC calculations
        if self.eesEMax == 0:
            self.eesEMax = 1
        # the amount of time in seconds that the EES must be able to discharge for at current level of SRC being provided
        self.eesSrcTime = float(eesSoup.eesSrcTime.get('value'))

        # the amount of time over which under SRC operation if recorded to see if go over limit eesUnderSrcLimit
        self.eesUnderSrcTime = float(eesSoup.eesUnderSrcTime.get('value'))
        # the limit in kW*s over essUnderSrcTime before underSRC flag is set.
        self.eesUnderSrcLimit = float(eesSoup.eesUnderSrcLimit.get('value'))

        # 'eesDispatchTime' is the minimum amount of time that the ESS must be able to supply the load for in order to
        # be considered as an active discharge option in the diesel schedule.
        self.eesDispatchTime = float(eesSoup.eesDispatchTime.get('value'))
        # 'eesDispatchMinSoc' is the minimum SOC of the ESS in order to be considered as an active discharge option in
        # the diesel schedule. Units are in pu of full energy capacity.
        #TODO commmented out because tag not in xml
        #self.eesDispatchMinSoc = float(eesSoup.eesDispatchMinSoc.get('value'))
        # In order to use the consider the equivalent fuel efficiency of dishcarging the ESS to allow running a smaller
        # diesel generator, an equivalent fuel consumption of the ESS must be calculated in kg/kWh. This is done by calculating
        # how much diesel fuel went into charging the ESS to it's current level. Divide the number of kg by the state of
        # charge to get the fuel consumption of using the energy storage.
        # 'prevEesTime' is how far back that is used to assess what percentage of the current ESS charge came from
        # the diesel generator. This is used in the dispatch schedule to determine the cost of discharging the ESS to supply
        # the load for peak shaving or load leveling purposes.
        self.prevEesTime = float(eesSoup.prevEesTime.get('value'))
        # 'eesCost' is the cost of discharging the ESS that is above the fuel cost that went into charging it. It is
        # stated as a fuel consumption per kWh, kg/kWh. It is added to the effective fuel consumption of discharging the
        # ESS resulting from chargning it with the diesel generators. The cost is used to account for non-fuel costs of
        # discharging the ESS including maintenance and lifetime costs. Units are kg/kWh.
        self.eesCost = float(eesSoup.eesCost.get('value'))
        # 'essChargeRate' is the fraction of power that it would take to fully charge or discharge the ESS that is the
        # maximum charge or discharge power. This creates charging and discharging curves that exponentially approach full
        # and zero charge.
        self.eesChargeRate = float(eesSoup.chargeRate.get('value'))
        # 'lossMapEstep' is the step interval that ePu will be interpolated along in the lossmap
        self.lossMapEstep = float(eesSoup.lossMapEstep.get('value'))
        # 'lossMapPstep' is the step interval that pPu will be interpolated along in the lossmap
        self.lossMapPstep = float(eesSoup.lossMapPstep.get('value'))
        # 'useLossMap' is a bool value that indicates whether or not use the lossMap in the simulation.
        self.useLossMap = eesSoup.useLossMap.get('value').lower() in ['true','1']

        if self.useLossMap:
            # handle the loss map interpolation
            # 'lossMap' describes the loss experienced by the energy storage system for each state of power and energy.
            # they are described by the tuples 'pPu' for power, 'ePu' for the state of charge, 'tempAmb' for the ambient
            # (outside) temperature and 'lossRate' for the loss. Units for power are P.U. of nameplate power capacity. Positive values
            # of power are used for discharging and negative values for charging. Units for 'ePu' are P.U. nameplate energy
            # capacity. It should be between 0 and 1. 'loss' should include all losses including secondary systems. Units for
            # 'loss' are kW.
            # initiate loss map class
            eesLM = esLossMap()
            pPu = np.array(readXmlTag(eesDescriptor,['lossMap','pPu'],'value','', 'float'))
            ePu = readXmlTag(eesDescriptor, ['lossMap', 'ePu'], 'value','',  'float')
            lossPu = readXmlTag(eesDescriptor, ['lossMap', 'loss'], 'value','',  'float')
            tempAmb = readXmlTag(eesDescriptor, ['lossMap', 'tempAmb'], 'value','',  'float')

            # convert per unit power to power
            P = np.array(pPu)
            P[P>0] = P[P>0]*self.eesPOutMax
            P[P<0] = P[P<0]*self.eesPInMax
            #convert per unit energy to energy
            E = np.array(ePu)*self.eesEMax
            # convert pu loss to power
            L = np.abs(np.array(lossPu) * P)

            lossMapDataPoints = []
            for idx, item in enumerate(pPu):
                lossMapDataPoints.append((float(P[idx]), float(E[idx]), float(L[idx]), float(tempAmb[idx])))

            eesLM.lossMapDataPoints = lossMapDataPoints
            eesLM.pInMax = self.eesPInMax
            eesLM.pOutMax = self.eesPOutMax
            eesLM.eMax = self.eesEMax
            # check inputs
            eesLM.checkInputs()
            # TODO: remove *2, this is for testing purposes
            # perform the linear interpolation between points, with an energy step every 1 kWh (3600 seconds)
            eesLM.linearInterpolation(self.eesChargeRate, eStep = self.lossMapEstep, pStep= self.lossMapPstep)

            self.eesLossMapP = eesLM.P
            # save the index of where the power vector is zero. This is used to speed up run time calculations
            self.eesLossMapPZeroInd = (np.abs(self.eesLossMapP)).argmin()
            self.eesLossMapE = eesLM.E
            self.eesLossMapTemp = eesLM.Temp
            self.eesLossMapLoss = eesLM.loss
            self.eesmaxDischTime = eesLM.maxDischTime
            self.eesNextBinTime = eesLM.nextBinTime
        else:
            self.eesLossMapP = []
            # save the index of where the power vector is zero. This is used to speed up run time calculations
            self.eesLossMapPZeroInd = 0
            self.eesLossMapE = []
            self.eesLossMapTemp = []
            self.eesLossMapLoss = []
            self.eesmaxDischTime = []
            self.eesNextBinTime = []



    def checkOperatingConditions(self, tIndex):
        """
        Checks if the ees is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        if self.eesState == 2: # if running online
            # find the loss at the current power and SOC state
            self.eesPloss = self.findLoss(self.eesP,self.timeStep)
            # update the SOC
            self.eesSOC = min([max([self.eesSOC - (self.eesP + self.eesPloss)*self.timeStep/self.eesEMax,0]),1])
            # find the amount of SRC power available
            self.updateSrcAvail()
            # find the available real power (reactive is set to max)
            self.eesPinAvail = self.findPchAvail(self.timeStep)
            self.eesPoutAvail = self.findPdisAvail(self.timeStep, 0, 0)
            # get the percent of the request SRC that is not being supplied.
            self.prevUnderSrc[tIndex] = max(self.eesSRC - self.eesPsrcAvail,0)
            # check if has operated more than eesUnderSrcLimit under the minimum SRC over the past eesUnderSrcTime
            if sum(self.prevUnderSrc[(tIndex-round(self.eesUnderSrcTime / self.timeStep)):tIndex])*self.timeStep > self.eesUnderSrcLimit:
                self.underSRC = True
            # check if the ees is discharging and not able to supply the full SRC requirements. If this is the case, then flag the underSRC flag
            elif (self.prevUnderSrc[tIndex] > 0) and (self.eesP > 0):
                self.underSRC = True
            else:
                self.underSRC = False

            # check to make sure the current power output or input is not greater than the maximum allowed.
            if (self.eesP > self.eesPoutAvail) | (self.eesP < -self.eesPinAvail):
                self.outOfBoundsReal = True
            else:
                self.outOfBoundsReal = False
            #TODO commmented out because tags not in xml
            # if (self.eesQ > self.eesQoutAvail) | (self.eesQ < -self.eesQinAvail):
            #     self.outOfBoundsReactive = True
            # else:
            #     self.outOfBoundsReactive = False

            self.eesRunTimeAct += self.timeStep
            self.eesRunTimeTot += self.timeStep
        elif self.eesState == 1: # if starting up
            self.eesPinAvail = 0 # not available to produce power yet
            self.eesPinAvail_1 = 0
            self.eesQinAvail = 0
            self.eesPoutAvail = 0  # not available to produce power yet
            self.eesQoutAvail = 0
            self.eesPoutAvailOverSrc = 0
            self.eesPoutAvailOverSrc_1 = 0
            self.eesStartTimeAct += self.timeStep
            self.eesRunTimeAct = 0 # reset run time counter
            self.underSRC = False
            self.outOfBoundsReal = False
            self.outOfBoundsReactive = False
        else: # if off
            # no power available and reset counters
            self.eesPinAvail = 0  # not available to produce power yet
            self.eesPinAvail_1 = 0
            self.eesQinAvail = 0
            self.eesPoutAvail = 0  # not available to produce power yet
            self.eesQoutAvail = 0
            self.eesPoutAvailOverSrc = 0
            self.eesPoutAvailOverSrc_1 = 0
            self.eesStartTimeAct = 0
            self.eesRunTimeAct = 0
            self.underSRC = False
            self.outOfBoundsReal = False
            self.outOfBoundsReactive = False

    # this finds the available charging power
    # duration is the duration that needs to be able to charge at that power for
    def findPchAvail(self, duration):
        if self.useLossMap:
            # get the index of the closest E from the loss map
            eInd = getIntListIndex(self.eesSOC*self.eesEMax, self.eesLossMapE, self.lossMapEstep)
            ChTimeSorted = self.eesmaxDischTime[:self.eesLossMapPZeroInd,eInd]
            # get the index of the closest discharge time to duration
            # need to reverse the order of discharge times to get
            dInd  = np.searchsorted(ChTimeSorted,duration,side='right')
            # the available charging power corresponds to the
            return -self.eesLossMapP[dInd]
        else:
            # charging power is simply amount of energy left till full divided by the duration
            return min([(1 - self.eesSOC)*self.eesEMax/duration, self.eesPInMax])

    # this finds the available discharge power
    # duration is the duration that needs to be able to discharge at that power for
    # kWreserved is the amount of charging power that is already spoken for
    # kWhReserved is the amount of energy that is already spoken for, for example for spinning reserve.  This must also
    # take into account the losses involved. For example, if for spinning reserve need to be able to discharge at 100 kW
    # for 180 sec, and at the current SOC this would result in 500 kWs of losses, then kWsReserved would be 18,500 kWs.
    # findLoss is a bool value. if True, the associated loss will be calculated for discharging at that power
    def findPdisAvail(self, duration, kWReserved, kWsReserved):
        if self.useLossMap:
            # get the index of the closest E from the loss map to the current energy state minus the reserved energy.
            # Subtracting the kWsReserved from the current SOC is not the most accurate way to do this, but it is a good
            # estimate. Ideally would search between current SOC down to kWsReserved, instead of of (current SOC -
            # kWsReserved) down to zero. However, this would not allow precalculating the matrix eesmaxDischTime.
            # TODO remove once other works
            #eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax - kWsReserved, side='left')

            # index of the energy closest to the current energy level stored
            eIndHere = getIntListIndex(self.eesSOC * self.eesEMax, self.eesLossMapE, self.lossMapEstep)
            #eIndHere = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
            # index of the energy required for SRC
            # TODO: consider saving this index to avoid this search
            eIndSrc = getIntListIndex(kWsReserved,self.eesLossMapE, self.lossMapEstep)
            #eIndSrc = np.searchsorted(self.eesLossMapE, kWsReserved, side='left')
            # get the searchable array for discharging power (positive). The discharge time is the difference between the
            # time to fully discharge the current energy bin and the time to fully discharge the energy bin required for
            # spinning reserve
            DisTimeSorted = self.eesmaxDischTime[self.eesLossMapPZeroInd + 1:, eIndHere] - \
                            self.eesmaxDischTime[self.eesLossMapPZeroInd + 1:, eIndSrc]
            # the discharge times for this are sorted in
            # decreasing order, so needs to be reversed
            DisTimeSorted = DisTimeSorted[::-1]
            dInd = np.searchsorted(DisTimeSorted, duration, side='right')
            # the index is from the back of the array, since was from a reversed array.
            # the maximum discharging power is the minimum of the power allowed to reserve the required capacity and the
            # difference between the maximum power and the reserved power in order to keep that power capability reserved.
            return min([self.eesLossMapP[-(dInd + 1)], self.eesPOutMax - kWReserved])
        else:
            # discharging power is simply the stored energy divided by duration
            return max([min([(self.eesSOC * self.eesEMax - kWsReserved)/ duration, self.eesPOutMax - kWReserved]),0])


    # findLoss returns the expected loss in kWs given a specific power and duration
    # P is the power expected to discharge at
    # duration is the time expected to discharge at P for
    def findLoss(self,P,duration):

        if self.useLossMap: # if use loss map, otherwise, no loss

            if P > 0: # if discharging
                # if the power is within the chargeRate and max discharge bounds
                #if (P <= self.eesSOC * self.eesEMax * self.eesChargeRate)  & P <= self.eesPOutMax:
                    # get the index of the closest E from the loss map to the current energy state minus the reserved energy
                    eInd = getIntListIndex(self.eesSOC * self.eesEMax, self.eesLossMapE, self.lossMapEstep)
                    # eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
                    # get index of closest P
                    pInd = getIntListIndex(P, self.eesLossMapP,self.lossMapPstep)
                    #pInd = np.searchsorted(self.eesLossMapP, P, side = 'left')
                    # create a cumulative sum of discharge times
                    # since discharging, the stored energy will be going down, thus reverse the order
                    times = self.eesNextBinTime[pInd,:eInd]
                    times = times[::-1]
                    cumSumTime = np.cumsum(times)
                    # get the index closest to the duration required
                    dInd = np.searchsorted(cumSumTime,duration)
                    return sum(self.eesLossMapLoss[pInd,(eInd-dInd-1):eInd])


            elif P < 0: # if charging
                # if the power is within the chargeRate and max discharge bounds
               # if (P >= (self.eesSOC - 1)*self.eesEMax  * self.eesChargeRate) & P >= -self.eesPInMax:
                    # get the index of the closest E from the loss map to the current energy state minus the reserved energy
                    eInd = getIntListIndex(self.eesSOC * self.eesEMax, self.eesLossMapE, self.lossMapEstep)
                    #eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
                    # get index of closest P
                    pInd = getIntListIndex(P, self.eesLossMapP, self.lossMapPstep)
                    #pInd = np.searchsorted(self.eesLossMapP, P, side='left')
                    # create a cumulative sum of discharge times
                    cumSumTime = np.cumsum(self.eesNextBinTime[pInd, eInd:])
                    # get the index closest to the duration required
                    dInd = np.searchsorted(cumSumTime, duration)
                    return sum(self.eesLossMapLoss[pInd, eInd:(eInd + dInd+1)])

            else: # if not doing anything
                return 0
        else:
            return 0

    # this will set the required SRC and find the minimum SOC that the ees must stay above to be able to supply the
    # required SRC
    def setSRC(self, SRC):
        # set the required SRC in kW
        self.eesSRC = SRC
        if self.useLossMap:
            # get index of closest P to SRC
            pInd = getIntListIndex(SRC, self.eesLossMapP, self.lossMapPstep)
            #pInd = np.searchsorted(self.eesLossMapP, SRC, side='left')
            #pInd = min([len(self.eesLossMapP)-1,pInd])
            # get the index of the closest max discharge time to the required SRC time
            eInd = np.searchsorted(self.eesmaxDischTime[pInd, :], self.eesSrcTime, side='left')
            eInd = min([len(self.eesLossMapE)-1, eInd])
            # set the required energy stored in the ees to supply the SRC, in kWs
            self.eesMinSrcE = self.eesLossMapE[eInd]
        else:
            self.eesMinSrcE = int(SRC*self.eesSrcTime)

    # this finds the available SRC given the current power
    def updateSrcAvail(self):
        useP = max([self.eesP,0]) # only take into account discharging power
        # SRC available includes reducing any charging - thus it is added in
        self.eesPsrcAvail = self.findPdisAvail(self.eesSrcTime, useP, useP*self.timeStep) - min([self.eesP,0])


    # this finds the power this ees is capable of being scheduled for.
    def updatePScheduleMax(self):
        self.eesPScheduleMax = self.findPdisAvail(self.eesDispatchTime, self.eesSRC, self.eesMinSrcE)