# Introduction
Control module input xml files are used to pass parameters to the [control modules](Model-Controls-Package) being run in a simulation. For example, parameters in `projectNameSetxGenDispatch0Inputs.xml` would be passed to the module `genDispatch0` (in `genDispatch0.py`) assuming that the [projectNameSetxSetup.xml](projectSetup-XML) indicated that `genDispatch0` was to be used instead of another generator dispatch such as `genDispatch1`, and where `projectName` and `x` are the project name and set identifier respectively. Each `control module` has a corresponding `control module inputs` XML file. 

Control module input files included are: 
* [projectGenDispatchInputs.xml](Model-Resources-Setup-projectGenDispatchInputs)
* [projectGenScheduleInputs.xml](Model-Resources-Setup-projectGenScheduleInputs)
* [projectEesDispatchInputs.xml](Model-Resources-Setup-projectEesDispatchInputs)
* [projectReDispatchInputs.xml](Model-Resources-Setup-projectReDispatchInputs)
* [projectTesDispatchIputs.xml](Model-Resources-Setup-projectTesDispatchInputs)
* [projectPredictLoadInputs.xml](Model-Resources-Setup-projectPredictLoadInputs)
* [projectPredictWindInputs.xml](Model-Resources-Setup-projectPredictWindInputs)
* [projectWtgDispatchInputs.xml](Model-Resources-Setup-projectWtgDispatchInputs)
* [projectGetMinSrcInputs.xml](Model-Resources-Setup-projectGetMinSrcInputs)
