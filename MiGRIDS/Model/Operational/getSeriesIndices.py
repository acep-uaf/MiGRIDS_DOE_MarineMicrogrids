# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 7, 2018
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np


def getSeriesIndices(steps, seriesLen):
    if steps == 'all' or steps == ':':
        idx = range(seriesLen)
    elif (type(steps) is list or type(steps) is np.ndarray):
        if len(steps) == 2:
            start = np.max([steps[0],0])
            stop = np.min([steps[-1],seriesLen-1])
            idx = range(start,stop)
        else:
            idx = steps
    elif type(steps) is int:
        stop = np.min([steps, seriesLen - 1])
        idx = range(stop)
    else:
        idx = steps

    return idx