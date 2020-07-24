Docker image development steps:

* Install Docker
  * [Download Docker CE Desktop for windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows) and install.
* Setup Windows Subsystem for Linux (WSL):
  * Install WSL Ubuntu 18.04
    * Open Powershell as **Administrator** and run:  
    `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
  * Open Windows App Store
    * Search for "Ubuntu" and install Ubuntu 18.04
* Launch WSL Ubuntu 18.04 and install docker
  * Install docker within WLS environment - [See Details](https://gist.github.com/dayne/313981bc3ee6dbf8ee57eb3d58aa1dc0#file-2-wsl-docker-md)
  * Connect WSL linux docker to the Windows Docker service
* Clone the repo
* Build a microgrids docker container
```
docker build . -t migrids
```
* Start hacking using the docker as the run environment.  For example here is a run of `TestScripts/generateRunsSandbox.py`
```
docker run -it -v ${PWD}:/migrids migrids python3 /migrids/TestScripts/generateRunsSandbox.py
```

---

Draft user instructions for using the tutorial data to test MiGRIDS.
* install docker
* download tutorial data and unzip to LOCATION
* set environment variable MIGRIDS_DATA=LOCATION
* create an alias for microgrids
  `alias microgrids='docker run -it -v $MIGRIDS_DATA:/data -v ${PWD}:/pwd migrids'`
* open (powershell) to the tutorial data
* run microgrids (set up an alias for microgrids docker run)

