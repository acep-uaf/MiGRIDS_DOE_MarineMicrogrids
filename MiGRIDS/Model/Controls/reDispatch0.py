# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: July 13, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
# import numpy as np

# this object dispatches units with a rule based system. Power setpoints to the wind turbine react slowly to the loading
# on the thermal energy storage system. The TES reacts quickly the the amount of wind power that can be accepted into the
# grid. This requires a TES to be part of the system.
class reDispatch:
    def __init__(self, args):
        self.wfPsetRatio = 0 # initiate the power output of the wind farm to zero
        self.wfPimport = 0 # initiate to zero
        self.wfP = 0 # total wind output
        self.wfPch = 0 # wf charging of eess
        self.wfPtess = 0 # wf charing to tess
        self.rePLimit = 0 # the max import allowed from renewables
        self.wfControlMaxRampRate = args['wfControlMaxRampRate']
        self.tessPset = args['tessPset']
        self.wfImportMaxRampRate = args['wfImportMaxRampRate']

    # FUTUREFEATURE: replace windfarm (wf) setpoints with a list of windturbine setpoints.
    def reDispatch(self, SO):
        """
        This dispatches the renewable energy in the grid.
        :param SO: pass the instance of the SystemOperations being run
        """
        ## get the current grid and wind conditions ##
        P = SO.P # current demand
        # wind turbine output is the min of available and setpoint
        # get available wind power
        wfPAvail = sum(SO.WF.wtgPAvail)

        ## calculate what the ideal wind import setpoint would be   ##
        # the maximum import
        self.rePLimit = P - sum(SO.PH.genMolAvail)
        # limit the change to the max wind import to not result in a greater ramp than allowed
        wfImportIdeal = max(min(self.wfPimport + self.wfImportMaxRampRate * SO.timeStep, self.rePLimit),
                            self.wfPimport - self.wfImportMaxRampRate * SO.timeStep)
        # calculate the ideal TES charging from wf
        wfPtessIdeal = SO.TESS.tesPInMax * self.tessPset
        # calculate the ideal charging of the EESS
        wfPeessIdeal  = sum(SO.EESS.eesPinAvail)
        # total wf ideal output power
        wfPIdeal = wfImportIdeal + wfPtessIdeal + wfPeessIdeal

        ## apply wf constraints on being able to reach that ideal power ##
        # calculate what fraction of total available wind power the ideal wind output is
        wfPsetRatioIdeal = min(wfPIdeal / max(wfPAvail,1), 1)
        # limit the change in wf output ratio to the max change in the ratio it is capable of
        self.wfPsetRatio = max(min(self.wfPsetRatio + self.wfControlMaxRampRate * SO.timeStep, wfPsetRatioIdeal),
                            self.wfPsetRatio - self.wfControlMaxRampRate * SO.timeStep)
        # calculate the resulting wind output power
        self.wfP = wfPAvail * self.wfPsetRatio

        ## calculate the resulting import, EESS charging and TES chargin ##
        # first pass at wf import. Will be recalculated later after actual charging is calculated
        wfPimportTest = min(wfImportIdeal,self.wfP)
        # calculate the resulting eess charging with the remaining available power
        self.wfPch = min(wfPeessIdeal,self.wfP - wfPimportTest)
        # dump the remaining power into the TESS, as much as possible
        self.wfPtess = min(SO.TESS.tesPInMax, self.wfP-wfPimportTest-self.wfPch)
        SO.TESS.runTesDispatch(self.wfPtess)
        # recalculate the total import.
        self.wfPimport = max(self.wfP - self.wfPch - self.wfPtess,0)
        # dispach the wf
        SO.WF.runWtgDispatch(self.wfP, 0, SO.masterIdx)


