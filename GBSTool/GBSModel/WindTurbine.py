# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup
from GBSAnalyzer.CurveAssemblers.wtgPowerCurveAssembler import WindPowerCurve


class WindTurbine:
    """
    Wind turbine class: contains all necessary information for a single wind turbine. Multiple wind turbines are
    aggregated in a Windfarm object (see Windfarm.py), which further is aggregated in the SystemOperations object (see
    SystemOperations.py).

    :param wtgID: internal id used in the Windfarm for tracking wind turbine objects. *type int*
    :var wtgName: name given in wtgDescriptor file and is merely uswed to trace back to that. *type string*
    :var wtgP: Current real power level, units: kW. *type float*
    :var wtgQ: Current reactive power level, units: kW. *type float*
    :var wtgState: Wind turbine operating state 0 - off, 1 - starting, 2 - online.
    :var wtgPMax: Real power nameplate capacity, units: kW. *type float*
    :var wtgQMax: Reactive power nameplate capacity, units: kvar. *type float*
    :var wtgPAvail: Available real power capacity, units: kW. *type float*
    :var wtgQAvail: Available reactive power capacity, units: kvar. *type float*
    :var wtgStartTime: Time to start the wind turbine, units: s. *type int*
    :var wtgPowerCurve: Power curve of the wind turbine, tuples of [kW, m/s]. *type list(float,float)*
    :var wtgRunTimeAct: Run time since last start, units: s. *type int*
    :var wtgRunTimeTot: Cummulative run time since model start, units: s. *type int*

    :method __init__: Constructor with additional instructions
    :method wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

    :returns:
    """

    # Wind turbine resources
    wtgID = None
    wtgName = None # This should come from the wtgDescriptor file and is merely uswed to trace back to that
    wtgP = 0 # Current real power level [kW]
    wtgQ = 0 # Current reactive power level [kW]
    wtgState = 0 # Wind turbine operating state [dimensionless, index]. See docs for key.
    wtgPMax = 0 # Nameplate capacity [kW]
    wtgQMax = 0 # Nameplate capacity [kvar]
    wtgPAvail = 0 # the available power from the wind [kW]
    wtgQAvail = 0 # the available power form the wind [kar]
    wtgStartTime = 0 # Time to start the wind turbine [s]
    # TODO: the power curve is not needed here, since will convert to P avail. remove.
    #wtgPowerCurve = [] # Power curve of the wind turbine, tuples of [kW, m/s]

    wtgRunTimeAct = 0 # Run time since last start [s]
    wtgRunTimeTot = 0 # Cummulative run time since model start [s]

    # Constructor
    def __init__(self, wtgID, wtgP, wtgQ, windSpeed, wtgDescriptor):
        """
        Constructor used for the initialization of an object within windfarm list of wind turbines.

        :param wtgID:
        :param wtgP:
        :param wtgQ:
        :param wtgDescriptor:
        """
        # Write initial values to internal variables.
        self.wtgID = wtgID
        self.wtgP = wtgP
        self.wtgQ = wtgQ
        wtgDescriptorParser(self, windSpeed, wtgDescriptor)

    def wtgDescriptorParser(self, windSpeed, wtgDescriptor):
        """
        wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

        :param wtgDescriptor: relative path and file name of wtgDescriptor.xml-file that is used to populate static
        information

        :return:
        """

        # read xml file
        wtgDescriptorFile = open(wtgDescriptor, "r")
        wtgDescriptorXml = wtgDescriptorFile.read()
        wtgDescriptorFile.close()
        wtgSoup = Soup(wtgDescriptorXml, "xml")


        # Dig through the tree for the required data
        self.wtgName = wtgSoup.component.get('name')
        self.wtgPMax = float(wtgSoup.POutMaxPa.get('value'))

        # Handle the fuel curve interpolation
        powerCurvePPuInpt = wtgSoup.powerCurveDataPoints.p.get('value').split()
        powerCurveWsInpt = wtgSoup.powerCurveDataPoints.ws.get('value').split()
        if len(powerCurvePPuInpt) != len(powerCurveWsInpt):  # check that both input lists are of the same length
            raise ValueError('Power curve calculation error: Power and wind speed lists are not of same length.')

        powerCurveData = []
        for idx, item in enumerate(powerCurvePPuInpt):
            powerCurveData.append((self.wtgPMax * float(powerCurvePPuInpt[idx]), float(powerCurveWsInpt[idx])))
        wtgPC = WindPowerCurve()
        wtgPC.powerCurveDataPoints = powerCurveData

        # TODO: continue to implement this