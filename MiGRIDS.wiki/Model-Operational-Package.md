The `Operational` package contains the following modules that control the running of simulations:

* [initiateProjectSet](Model-initiateProjectSet): This is used to initiate a new set of simulations within a project. 
* [generateRuns](Model-Operational-generateRuns): Once a set has been initiated, this will created the files for each simulation run within the simulation set. 
* [runSimulation](Model-Operational-runSimulation): Once the simulation run files have been generated, this will run them. 
* [SystemOperations](Model-Operational-SystemOperations): This called by `runSimulation` to run the simulations
