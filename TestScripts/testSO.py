# -*- coding: utf-8 -*-
"""
Created on Mon May 16 15:35:49 2022

@author: Nathan Green
"""
def testDiesCapReqCalc(eesPsrcAvail, srcMin, wtgPAvail, wtgP, wtgMinSrcCover, phP):
    usedUpEessSrc = min(eesPsrcAvail,srcMin)
    wtgSpilled = wtgPAvail-wtgP
    if wtgSpilled > 0:
        wtgSpilledSRC = (wtgPAvail-wtgP)*wtgMinSrcCover 
        wtgSrcAvg = wtgSpilledSRC / wtgSpilled
        if wtgSrcAvg > 0:
            wtgThatCanBeCoveredByEESS = (eesPsrcAvail - usedUpEessSrc) / wtgSrcAvg
        else:
            wtgThatCanBeCoveredByEESS = wtgSpilled
    else:
        wtgSpilled = 0
        wtgThatCanBeCoveredByEESS = 0
    dieselCapRequired = round(max(srcMin - usedUpEessSrc + phP - min(wtgSpilled,wtgThatCanBeCoveredByEESS),0))
    
    return dieselCapRequired
    

if __name__=='__main__':
    # # No GBS
    # eesPsrcAvail = [0.0]
    # srcMin = [523.881, 523.881]
    # wtgPAvail = [396.0]
    # wtgP = [396.0]
    # wtgMinSrcCover = [1.0]
    # # phP
    # # GBS
    # eesPsrcAvail = [1083.3333333]
    # srcMin = [523.881, 523.881]
    # wtgPAvail = [396.0]
    # wtgP = [396.0]
    # wtgMinSrcCover = [1.0]
    # phP = 839.54
    
    # No GBS
    eesPsrcAvail = 0.0
    load = 675.0
    wtgP = 275.0
    wtgPAvail = 900.0
    wtgMinSrcCover = 0.05
    loadminSRC = load*0.1
    wtgminSRC = wtgMinSrcCover*wtgP
    srcMin = loadminSRC + wtgminSRC

    phP = load - wtgP
    dieselCapRequired = testDiesCapReqCalc(eesPsrcAvail, srcMin, wtgPAvail, 
                                           wtgP, wtgMinSrcCover, phP)
    print(dieselCapRequired)