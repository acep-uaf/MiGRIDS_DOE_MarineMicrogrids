# Project: MiGRIDS
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: January 19, 2022
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate a short term future Wind power
class windPredict:

    def __init__(self,args):
        self.futureWind = [0]
        self.std = args['std']
        self.nearTermWindow = args['nearTermWindow']
    def windPredict(self, SO):
        self.futureWind = []
        self.futureWindNearTerm = []
        #startIdx10min = max(SO.idx - int(600/SO.timeStep),0)
        #stopIdx = SO.idx + 1
        # for each wind turnbine
        error = np.random.randn()*self.std
        for wtg in SO.WF.windTurbines:
            #self.futureWind += [wtg.windPower10minTrend[SO.masterIdx]]
            self.futureWindNearTerm += [min(wtg.windPower[SO.masterIdx:int(SO.masterIdx+self.nearTermWindow/SO.timeStep)])*(1+error)]

        self.futureWind = self.futureWindNearTerm