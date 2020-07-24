The Model Package contains code that is core to running a single simulation of a time-series energy balance model (TSEBM). It also contains several sub-packages with resources for correct model setup. 

During a time-step in the TSEMB the system calculates the energy balance, then checks if the current system state infringes on given boundary conditions that should trigger a transition in system state. If a such a condition is triggered either a timer is started (straight time or cumulative energy over a maximum time) or a system state transition is triggered (either because a timer is expired, or because immediate action is required when a particular condition is met). System state transitions require dispatch decisions to be made. The figure shows the conceptual flow of a model time-step. 

![Conceptual Flow of a TSEBM time-step](https://user-images.githubusercontent.com/11688057/33266158-aa96e566-d374-11e7-8747-8fd723c3db8a.png)

A detailed list of operating conditions and triggers is compiled in [this Wiki-page](Model-Package-Triggers/)

The Model package is broken into several subpackages: 
* The [Control Package](Model-Controls-Package) contains the controllers that dispatch (send power setpoints), schedule (bring components on and offline) and predict future variable generation and load. 
* The [Components Package](Model-Components-Package) contains the hierarchical classes of individual components (such as a wind turnbine of diesel generator) and systems of individual components (such as a wind farm or a powerhouse). 
* The [Operational Package](Model-Operational-Package) contains the modules that run the simulations. 
* The [Resources Package](Model-Resources-Package) contains the XML files that are copied to a project directory and contain the information on which modules are run in a simulation and their input parameters. 

