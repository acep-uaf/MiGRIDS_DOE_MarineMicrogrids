# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 10:42:30 2021

@author: Nathan Green
"""
import os
from MiGRIDS.Model.Components.Powerhouse import Powerhouse

if __name__ == '__main__':
    projectName = 'XYZ'
    setNum = 'Set0'
    currentPath = os.path.dirname(os.path.abspath(__file__))
    projectPath = os.path.join(currentPath, '..', '..', '..',
                               'MiGRIDSProjects', 'XYZ')
    filePath = os.path.join(currentPath, '..', 'Controls')
    genIDS = list(range(3))
    genStates = [2, 2, 1]
    timeStep = 10
    genDescriptor = [os.path.join(projectPath, 'InputData', 'Components', 'gen0Descriptor.xml'),
                     os.path.join(projectPath, 'InputData', 'Components', 'gen1Descriptor.xml'),
                     os.path.join(projectPath, 'InputData', 'Components', 'gen2Descriptor.xml')]
    genDispatchFile = os.path.join(filePath, 'genDispatch0.py',)
    genScheduleFile = os.path.join(filePath, 'genSchedule1.py')
    genDispatchInputsFile = os.path.join(projectPath, 'OutputData', setNum, 'Setup',
                                         projectName+setNum+'GenDispatch0Inputs.xml')
    genScheduleInputsFile = os.path.join(projectPath, 'OutputData', setNum, 'Setup',
                                         projectName+setNum+'GenSchedule1Inputs.xml')
    ph = Powerhouse(genIDS, genStates, timeStep, genDescriptor, genDispatchFile, genScheduleFile,
                    genDispatchInputsFile, genScheduleInputsFile)