# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

import glob
# imports
import os
import sqlite3
import sys
import re
import numpy as np
import pandas as pd
import pickle

from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllRuns
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from MiGRIDS.Analyzer.DataRetrievers.readNCFile import readNCFile
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Analyzer.PerformanceAnalyzers.getRunFuelUse import getRunFuelUse


def fillRunMetaData(projectSetDir, runs):
    '''Fills results into the database to be displayed graphically or passed to other analysis
    :param projectSetDir String path to directory for a specified set
    :param runs list of integers indicating the run numbers to process. If empty will process all runs within a set'''
    # get the set number
    setName = os.path.basename(projectSetDir)
    setNum = str(setName[3:])
    dbhandler = ProjectSQLiteHandler()
    dbhandler.prepareForResults(projectSetDir)
    # read the input parameter sql database


    # add columns for results - don't need if writing directly to run table
    # df = pd.DataFrame(
    #     columns=
    genOverLoading = []
    eessOverLoading = []



    # check which runs to analyze
    if not runs:
        runs = getAllRuns(projectSetDir)

    for runNum in runs:
        eessOL, genOL, valuesDictionary = getRunMetadata(projectSetDir, runNum, setNum)
        genOverLoading = genOverLoading + genOL
        eessOverLoading = eessOverLoading + eessOL

        dbhandler.updateRunResult(setNum,runNum,valuesDictionary)


    return eessOverLoading,genOverLoading


def preserveRunMetadata(eessOverLoading,genOverLoading,projectSetDir):
    generateOverLoadResults(eessOverLoading, genOverLoading, projectSetDir)
    setNum = re.findall('Set[0-100]',projectSetDir)[0]
    exportRunMetadata(setNum)

def exportRunMetadata(setNum):
    dbhandler = ProjectSQLiteHandler()
    dbhandler.exportRunMetadata(setNum)
    del dbhandler

def getRunMetadata(projectSetDir, runNum, setNum):
    # get run dir
    projectRunDir = os.path.join(projectSetDir, 'Run' + str(runNum))
    # go to dir where output files are saved
    # os.chdir(os.path.join(projectRunDir, 'OutputData'))
    runOutputDir = os.path.join(projectRunDir, 'OutputData')
    # load the total powerhouse output
    genPStats, genP, ts = loadResults('powerhousePSet' + str(setNum) + 'Run' + str(runNum) + '.nc', runOutputDir)
    # load the total powerhouse charging of eess
    genPchStats, genPch, ts = loadResults('powerhousePchSet' + str(setNum) + 'Run' + str(runNum) + '.nc',
                                          runOutputDir)
    # get generator power available stats
    genPAvailStats, genPAvail, tsGenPAvail = loadResults('genPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc',
                                                         runOutputDir)
    # check to see if fuel consumption has been calculated
    genFuelConsFileNames = glob.glob(os.path.join(runOutputDir, 'gen*FuelConsSet*Run*.nc'))
    # if the fuel cons has not been calculated, calculate
    if len(genFuelConsFileNames) == 0:
        getRunFuelUse(projectSetDir, [runNum])
        genFuelConsFileNames = glob.glob(os.path.join(runOutputDir, 'gen*FuelConsSet*Run*.nc'))
    # iterate through all generators and sum their fuel consumption.
    genFuelCons = 0
    for genFuelConsFileName in genFuelConsFileNames:
        genFuelConsStats0, genFuelCons0, ts = loadResults(genFuelConsFileName, runOutputDir)
        # genFuelCons
        genFuelCons = genFuelCons + genFuelConsStats0[4]
    # calculate the average loading while online
    idxOnline = [idx for idx, x in enumerate(genPAvail) if x > 0]  # the indices of when online
    # the loading profile of when online
    genLoading = [x / genPAvail[idxOnline[idx]] for idx, x in enumerate(genP[idxOnline])]
    genLoadingMean = np.mean(genLoading)
    genLoadingStd = np.std(genLoading)
    genLoadingMax = np.max(genLoading)
    genLoadingMin = np.min(genLoading)
    # the online capacity of diesel generators
    genCapacity = genPAvail[idxOnline]
    genCapacityMean = np.mean(genCapacity)
    # get overloading of diesel
    # get indicies of when diesel generators online
    idxGenOnline = genPAvail > 0
    genOverLoadingTime = np.count_nonzero(genP[idxGenOnline] > genPAvail[idxGenOnline]) * ts / 3600
    genLoadingDiff = genP[idxGenOnline] - genPAvail[idxGenOnline]
    genOverLoading = [[x for x in genLoadingDiff if x > 0]]
    genOverLoadingkWh = sum(genLoadingDiff[genLoadingDiff > 0]) * ts / 3600
    # get overloading of the ESS. this is the power requested from the diesel generators when none are online.
    # to avoid counting instances where there there is genP due to rounding error, only count if greater than 1
    eessOverLoadingTime = sum([1 for x in genP[~idxGenOnline] if abs(x) > 1]) * ts / 3600
    eessOverLoadingkWh = sum([abs(x) for x in genP[~idxGenOnline] if abs(x) > 1]) * ts / 3600
    eessOverLoading = [[x for x in genP[~idxGenOnline] if abs(x) > 1]]
    # get the total time spend in diesel-off
    genTimeOff = np.count_nonzero(genPAvail == 0) * tsGenPAvail / 3600
    # get the total diesel run time
    genTimeRunTot = 0.
    genRunTimeRunTotkWh = 0.
    for genRunTimeFile in glob.glob(os.path.join(runOutputDir, 'gen*RunTime*.nc')):
        genRunTimeStats, genRunTime, ts = loadResults(genRunTimeFile, runOutputDir)
        genTimeRunTot += np.count_nonzero(genRunTime != 0) * ts / 3600
        # get the capcity of this generator
        # first get the gen ID
        genID = re.search('gen(.*)RunTime', genRunTimeFile).group(1)
        genPMax = readXmlTag("gen" + genID + "Set" + str(setNum) + "Run" + str(runNum) + "Descriptor.xml",
                             "POutMaxPa",
                             "value", fileDir=projectRunDir + "/Components", returnDtype='float')
        genRunTimeRunTotkWh += (np.count_nonzero(genRunTime != 0) * ts / 3600) * genPMax[0]
    # calculate total generator energy delivered in kWh
    genPTot = (genPStats[4] - genPchStats[4]) / 3600
    # calculate total generator energy delivered in kWh
    genPch = (genPchStats[4]) / 3600
    # calculate generator switching
    genSw = np.count_nonzero(np.diff(genPAvail))
    # load the wind data
    wtgPImportStats, wtgPImport, ts = loadResults('wtgPImportSet' + str(setNum) + 'Run' + str(runNum) + '.nc',
                                                  runOutputDir)
    wtgPAvailStats, wtgPAvail, ts = loadResults('wtgPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc',
                                                runOutputDir)
    wtgPchStats, wtgPch, ts = loadResults('wtgPchSet' + str(setNum) + 'Run' + str(runNum) + '.nc', runOutputDir)
    # tes
    # get tess power, if included in simulations
    if len(glob.glob(os.path.join(runOutputDir, 'ees*SRC*.nc'))) > 0:
        tessPStats, tessP, ts = loadResults('tesPSet' + str(setNum) + 'Run' + str(runNum) + '.nc', runOutputDir)
        tessPTot = tessPStats[4] / 3600
    else:
        tessPStats = [0, 0, 0, 0, 0]
    # spilled wind power in kWh
    wtgPspillTot = (wtgPAvailStats[4] - wtgPImportStats[4] - wtgPchStats[4] - tessPStats[4]) / 3600
    # imported wind power in kWh
    wtgPImportTot = wtgPImportStats[4] / 3600
    # windpower used to charge EESS in kWh
    wtgPchTot = wtgPchStats[4] / 3600
    # eess
    # get eess power
    eessPStats, eessP, ts = loadResults('eessPSet' + str(setNum) + 'Run' + str(runNum) + '.nc', runOutputDir)
    # get the charging power
    eessPch = [x for x in eessP if x < 0]
    eessPchTot = -sum(eessPch) * ts / 3600  # total kWh charging of eess
    # get the discharging power
    eessPdis = [x for x in eessP if x > 0]
    eessPdisTot = (sum(eessPdis) * ts) / 3600  # total kWh dischargning of eess
    # get eess SRC
    # get all ees used in kWh
    eessSRCTot = 0
    for eesFile in glob.glob(os.path.join(runOutputDir, 'ees*SRC*.nc')):
        eesSRCStats, eesSRC, ts = loadResults(eesFile, runOutputDir)
        eessSRCTot += eesSRCStats[4] / 3600
    # TODO: add gen fuel consumption
    # add row for this run
    # df.loc[runNum] = [genPTot,genPch,genSw,genLoadingMean,genCapacityMean,genFuelCons,genTimeOff,genTimeRunTot,genRunTimeRunTotkWh,genOverLoadingTime,genOverLoadingkWh,wtgPImportTot,wtgPspillTot,wtgPchTot,eessPdisTot,eessPchTot,eessSRCTot,eessOverLoadingTime,eessOverLoadingkWh,tessPTot]
    valuesDictionary = {'genPTot': genPTot, 'genPch': genPch, 'genSw': genSw,
                        'genLoadingMean': genLoadingMean, 'genCapacityMean': genCapacityMean,
                        'genFuelCons': genFuelCons,
                        'genTimeOff': genTimeOff, 'genTimeRunTot': genTimeRunTot,
                        'genRunTimeRunTotkWh': genRunTimeRunTotkWh,
                        'genOverLoadingTime': genOverLoadingTime, 'genOverLoadingkWh': genOverLoadingkWh,
                        'wtgPImportTot': wtgPImportTot,
                        'wtgPspillTot': wtgPspillTot, 'wtgPchTot': wtgPchTot, 'eessPdisTot': eessPdisTot,
                        'eessPchTot': eessPchTot,
                        'eessSRCTot': eessSRCTot, 'eessOverLoadingTime': eessOverLoadingTime,
                        'eessOverLoadingkWh': eessOverLoadingkWh,
                        'tessPTot': tessPTot}

    return eessOverLoading, genOverLoading, valuesDictionary

def generateOverLoadResults(eessOverLoading, genOverLoading, runOutputDir):
    # make pdfs
    # generator overloading
    # get all simulations that had some generator overloading
    genOverloadingSims = [x for x in genOverLoading if len(x) > 0]
    if len(genOverloadingSims) > 0:
        maxbin = max(max(genOverloadingSims))
        minbin = min(min(genOverloadingSims))
        genOverLoadingPdf = [[]] * len(genOverLoading)
        for idx, gol in enumerate(genOverLoading):
            genOverLoadingPdf[idx] = np.histogram(gol, 10, range=(minbin, maxbin))
    else:
        genOverLoadingPdf = []

    outfile = open(os.path.join(runOutputDir, 'genOverLoadingPdf.pkl'), 'wb')
    pickle.dump(genOverLoadingPdf, outfile)
    outfile.close()
    # eess overloading
    eessOverLoadingSims = [x for x in eessOverLoading if len(x) > 0]
    if len(eessOverLoadingSims) > 0:
        maxbin = max(max(eessOverLoadingSims))
        minbin = min(min(eessOverLoadingSims))
        eessOverLoadingPdf = [[]] * len(eessOverLoading)
        for idx, eol in enumerate(eessOverLoading):
            eessOverLoadingPdf[idx] = np.histogram(eol, 10, range=(minbin, maxbin))
    else:
        eessOverLoadingPdf = []
    outfile = open(os.path.join(runOutputDir, 'eessOverLoadingPdf.pkl'), 'wb')
    pickle.dump(eessOverLoadingPdf, outfile)
    outfile.close()
    return


def loadResults(fileName, location = '', returnTimeSeries = False):

    var = readNCFile(os.path.join(location,fileName))
    val = np.array(var.value)*var.scale + var.offset
    timeStep = np.nanmean(np.diff(var.time)) # mean timestep in seconds
    valMean = np.nanmean(val)
    valSTD = np.nanstd(val)
    valMax = np.nanmax(val)
    valMin = np.nanmin(val)
    valInt = np.nansum(val)*timeStep # the integral over seconds. If the value is in kW, this is kWs.

    if returnTimeSeries is False:
        return [valMean, valSTD, valMax, valMin, valInt], val, timeStep
    else:
        return [valMean, valSTD, valMax, valMin, valInt], val, var.time
