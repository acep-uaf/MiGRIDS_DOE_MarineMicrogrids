
from MiGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../MiGRIDSProjects/SampleProject1/OutputData/Set0")
runs = []
getRunMetaData(projectSetDir,[])

