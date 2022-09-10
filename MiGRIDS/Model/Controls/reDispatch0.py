# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: July 13, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# this object dispatches units with a rule based system. Power setpoints to the wind turbine react slowly to the loading
# on the thermal energy storage system. The TES reacts quickly the the amount of wind power that can be accepted into the
# grid. This requires a TES to be part of the system.
class reDispatch:
    def __init__(self, args):
        self.wfPsetRatio = 0 # initiate the power output of the wind farm to zero
        self.wfPimport = 0 # initiate to zero
        self.wfControlMaxRampRate = args['wfControlMaxRampRate']
        self.tessPset = args['tessPset']
        self.wfImportMaxRampRate = args['wfImportMaxRampRate']

    # FUTUREFEATURE: replace windfarm (wf) setpoints with a list of windturbine setpoints.
    def reDispatch(self, SO):
        """
        This dispatches the renewable energy in the grid.
        :param OS: pass the instance of the SystemOperations being run
        :param P: the current load
        :param wfPset: the power setpoints for each wind turbine
        """
        P = SO.P # current demand
        # wind turbine output is the min of available and setpoint
        # get available wind power
        wfPAvail = sum(SO.WF.wtgPAvail)
        # this is the actual output of the wind turbine
        self.wfP = min(wfPAvail, self.wfPsetRatio*wfPAvail)
        # dispach the wf
        SO.WF.runWtgDispatch(self.wfP,0, SO.masterIdx)

        # the max that can be imported is the minimum between the difference between load and MOL, and ramp constraints
        self.rePLimit = max(min(self.wfPimport + self.wfImportMaxRampRate * SO.timeStep, P - sum(SO.PH.genMolAvail)),0)

        # amount of imported wind power
        self.wfPimport = min(self.rePLimit, self.wfP)

        # charge the EESS with whatever is leftover, as much as possible.
        # amount of wind power used to charge the eess is the minimum of maximum charging power and the difference
        # between available wind power and wind power imported to the grid.
        self.wfPch = min(sum(SO.EESS.eesPinAvail), self.wfP - self.wfPimport)

        # Any leftover needs to be dumped into the TES, up to maximum power
        self.wfPtess = min(SO.TESS.tesPInMax, self.wfP-self.wfPimport-self.wfPch)
        # FUTUREFEATURE: replace this with a proper calc
        SO.TESS.runTesDispatch(self.wfPtess)
        # recalculate imported wind based on ability of TESS to regulate
        self.wfPimport = self.wfP - self.wfPch - self.wfPtess


        # the difference between wind charging of TESS and import and the setpoints.
        wfOverProduction = self.wfPtess - SO.TESS.tesPInMax * self.tessPset + self.wfPimport - self.rePLimit

        # calculate the change in wtg setpoint
        wfPchange = min([SO.WF.wtgPMax *self.wfControlMaxRampRate*SO.timeStep, wfOverProduction], key=abs)

        self.wfPsetRatio = max(min(self.wfPsetRatio*wfPAvail - wfPchange, wfPAvail), 0) / max(wfPAvail, 1) # ratio of wind sepoint to available wind





