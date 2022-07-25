# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 10:42:30 2021

@author: Nathan Green
"""
import os
import matplotlib.pyplot as plt
import numpy as np
from MiGRIDS.Model.Components.Powerhouse import Powerhouse

if __name__ == '__main__':
    plotFuelCurves = True
    projectName = 'MIRACLBaseline'
    setNum = 'Set0'
    runNum = 'Run0'
    currentPath = os.path.dirname(os.path.abspath(__file__))
    projectPath = os.path.abspath(os.path.join(currentPath, '..',
                                               'MiGRIDSProjects', projectName))
    filePath = os.path.join(currentPath, '..', 'MiGRIDS', 'Model', 'Controls')
    # genIDS = list(range(3))
    genIDS = ['0', '1', '2']
    genStates = [1, 0, 0]
    onlineID = 4
    timeStep = 10
    genDescriptor = [os.path.join(projectPath, 'OutputData', setNum, runNum, 'Components',
                                  'gen0'+setNum+runNum+'Descriptor.xml'),
                     os.path.join(projectPath, 'OutputData', setNum, runNum, 'Components',
                                  'gen1'+setNum+runNum+'Descriptor.xml'),
                     os.path.join(projectPath, 'OutputData', setNum, runNum, 'Components',
                                  'gen2'+setNum+runNum+'Descriptor.xml')]
    genDispatchFile = os.path.join(filePath, 'genDispatch0.py',)
    genScheduleFile = os.path.join(filePath, 'genSchedule1.py')
    genDispatchInputsFile = os.path.join(projectPath, 'OutputData', setNum, 'Setup',
                                         projectName+setNum+'GenDispatch0Inputs.xml')
    genScheduleInputsFile = os.path.join(projectPath, 'OutputData', setNum, 'Setup',
                                         projectName+setNum+'GenSchedule1Inputs.xml')
    ph = Powerhouse(genIDS, genStates, timeStep, genDescriptor, genDispatchFile, genScheduleFile,
                    genDispatchInputsFile, genScheduleInputsFile)
    
    futureLoad = 505
    futureRE = 0
    scheduledSRCSwitch = 0.0
    scheduledSRCStay = 0.0
    powerAvailToSwitch = 0
    powerAvailToStay = 256.519
    underSRC = False
    
    # ph.genSchedule.minimizeFuel = True
        
    
    for futureLoad in range(2250):
        for idx, gen in enumerate(ph.generators):
            gen.genRunTimeAct = 5600  # Run time since last start [s]
            gen.genRunTimeTot = 5600  # Cummulative run time since model start [s]
            gen.genStartTimeAct = 30  # the amount of time spent warming up
            gen.genState=genStates[idx]
            gen.updateGenPAvail()
            gen.checkOperatingConditions()
        ph.onlineCombinationID = onlineID
        ph.runGenDispatch(futureLoad - futureRE, 0)
        ph.runGenSchedule(futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay,
                          powerAvailToSwitch, powerAvailToStay,underSRC)
    
    # print([gen.genState for gen in ph.generators])
    
    if plotFuelCurves:
        for idx in ph.combinationsID:
            x, y = list(zip(*ph.genCombinationsFCurve[idx]))
            plt.plot(x, y, label=idx)
            plt.ylabel('Fuel Rate (kg/s)')
            plt.xlabel('Generator Output (kW)')
            plt.title('Fuel Consumption by Gen Combination')
            
        plt.legend()
    
    # prevgencombo = -1
    # for pwr, FCompList in ph.lkpMinFuelConsumption.items():
    #     minfuelidx = np.argmin(FCompList)
    #     gencombo = ph.lkpMinFuelConsumptionGenID[pwr][minfuelidx]
        
    #     if (not pwr) or (not np.equal(prevgencombo, gencombo)):
    #         print('Gen Combo', gencombo, 'starts at', pwr, 'kW')
    #     # print('   ', idx, x)
    #     prevgencombo = gencombo
    # ph.importUserDefinedSchedule(os.path.join(projectPath, 'OutputData', setNum, runNum, 'Components'),
    #                              fileName='minFuelGenSchedule.csv')
    
    