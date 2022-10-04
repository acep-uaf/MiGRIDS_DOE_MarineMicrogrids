# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: 09/28/2022
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate the minimum required src

class getMinSrc:

    def __init__(self, args):
        self.minSRCToSwitchRatio = args['minSRCToSwitchRatio']
        self.ruleCurveWindPU = args['ruleCurveWindPU']
        self.ruleCurveMinSrcPU = args['ruleCurveMinSrcPU']
        self.ruleCurveWindPU = [float(a) for a in self.ruleCurveWindPU.split(' ')]
        self.ruleCurveMinSrcPU = [float(a) for a in self.ruleCurveMinSrcPU.split(' ')]
        self.minSrcToStay = 0
        self.minSrcToSwitch = 0
        # fill out the rule curve with interpolation
        self.ruleCurveWindPuFilled = np.linspace(0,self.ruleCurveWindPU[-1],num=101)
        self.ruleCurveMinSrcPuFilled = np.interp(self.ruleCurveWindPuFilled,self.ruleCurveWindPU,self.ruleCurveMinSrcPU)

    def getMinSrc(self, SO, calcFuture = False, nearTerm = False):

        # Take the average load of this hour last week 24.5hr * 3600 s/hr = 617400s , 23.5hr * 3600 = 592200
        # try with and without, compare the difference in performance.
        #meanLastWeek = np.mean(prevLoad[int(-617400/timeStep):int(-592200/timeStep)])
        # if a list is given for prevLoad, get mean value, otherwise, use the value given

        if calcFuture and not nearTerm:
            # the minimum src required.
            # find the current wind PU
            windPU = [np.min([1,a/b.wtgPMax]) for a, b in zip(SO.futureWind, SO.WF.windTurbines)]
            # fing the idx of the corresponding rule curve
            windIdx = [np.digitize(a,self.ruleCurveWindPuFilled, right=True) for a in windPU]
            # get the total min SRC required
            self.minSrcToStay = SO.futureLoad * SO.DM.minSRC + sum([self.ruleCurveMinSrcPuFilled[a]*float(b)
                                                                    for a, b in zip(windIdx, SO.futureWind)])
            # when scheduling new units online, use a higher SRC in order to avoid having just enough power to cover SRC required
            # and then have the requirement increase
            self.minSrcToSwitch = self.minSrcToStay * self.minSRCToSwitchRatio
        elif calcFuture and nearTerm:
            # find the current wind PU
            windPU = [np.min([1, a / b.wtgPMax]) for a, b in zip(SO.futureWindNearTerm, SO.WF.windTurbines)]
            # fing the idx of the corresponding rule curve
            windIdx = [np.digitize(a, self.ruleCurveWindPuFilled, right=True) for a in windPU]
            # get the total min SRC required
            self.minSrcToStay = SO.futureLoad * SO.DM.minSRC + sum([self.ruleCurveMinSrcPuFilled[a]*float(b)
                                                                    for a, b in zip(windIdx,SO.futureWindNearTerm)])

            self.minSrcToSwitch = self.minSrcToStay * self.minSRCToSwitchRatio

        else:

            meanLastTenMin = SO.DM.realLoad10minTrend[SO.masterIdx] #np.mean(SO.DM.realLoad[max((SO.idx - int(600/SO.timeStep)), 0):(SO.idx+1)])

            # the minimum src required.
            # remove non firm power from the SRC requirements
            if hasattr(SO,'TESS'):
                nonFirmWtgP = SO.reDispatch.wfPch + sum(SO.TESS.tesP)
            else:
                nonFirmWtgP = SO.reDispatch.wfPch

            # find the current wind PU
            windPU = [np.min([1, a / b.wtgPMax]) for a, b in zip(SO.WF.wtgP, SO.WF.windTurbines)]
            # fing the idx of the corresponding rule curve
            windIdx = [np.digitize(a, self.ruleCurveWindPuFilled, right=True) for a in windPU]
            # get the total min SRC required
            self.minSrcToStay = meanLastTenMin*SO.DM.minSRC + sum(
                [self.ruleCurveMinSrcPuFilled[a]*float(b) for a,b in zip(windIdx,SO.WF.wtgP)])*\
                                (1 - nonFirmWtgP/max(sum(SO.WF.wtgP),1))

            # when scheduling new units online, use a higher SRC in order to avoid having just enough power to cover SRC required
            # and then have the requirement increase
            self.minSrcToSwitch = self.minSrcToStay*self.minSRCToSwitchRatio
