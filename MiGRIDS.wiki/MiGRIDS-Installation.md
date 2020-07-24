MiGRIDS is written in Python3 and requires NetCDF and HDF5 libraries for data access.

We have instructions here for [Linux (Ubuntu)](#ubuntu-setup) and [Windows](#windows-setup) using Windows Subsystem for Linux.  If you are interested in setting up MiGRIDS on another platform please contact us and we'll work with you to document the setup process and add those instructions here.

## Ubuntu Setup

Setting up MiGRIDS on a modern Ubuntu system is straight forward.  The following instructions work for Ubuntu 18.04 or newer. 

**Install minimum system package dependencies:**

```
sudo apt update 
sudo apt upgrade -y
sudo apt install python3-h5netcdf python3-netcdf4 python3-pandas  \
         python3-distutils git tmate
```

You system now has the needed dependencies for MiGRIDS.

### Download MiGRIDs

The following instructions downloads, via git, the latest version of MiGRIDS.  

You will need to add the location you put MiGRIDS to your `PYTHONPATH` environment variable, the echo line will add that to your `.bashrc`.

```
git clone https://github.com/acep-uaf/MiGRIDS.git
cd MiGRIDS
echo "export MIGRIDS=${PWD}" >> ${HOME}/.bashrc
echo 'export PYTHONPATH=${PYTHONPATH}:${MIGRIDS}' >> ${HOME}/.bashrc
```

**Note:** Logout of this session and login again to ensure PYTHONPATH is set correctly.

> You can verify the environmental setting for MiGRIDS was set correctly by with: 
> ```sh
> echo $MIGRIDS
> echo $PYTHONPATH
> ```

Verify MiGRIDS is able to run with our sanity check script:

```
./TestScripts/sanity-check.sh
```

## Windows Setup

We recommend using the new [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10). 

### Windows Subsystem for Linux Install

1) Open Powershell as Administrator and run:  
  `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
2) Open Windows App Store and search for `Ubuntu`.  Install the `Ubuntu 18.04` package.
3) Open Ubuntu 18.04 - the first launch will take some time.  
  * Once open right click on the task bar icon and `pin to taskbar`.  

Once that is completed you can follow along, exactly, the steps for an [Ubuntu Setup](#ubuntu-setup). However if you want a more integrated with your Windows environment we recommend doing the following steps.

```
ln -s /mnt/c/Users/WINDOWS_USERNAME_HERE/Documents .
cd Documents
```

You are now ready to run through the [Ubuntu Setup](#ubuntu-setup) instructions.

Once you have done that, including the logout/login step, we recommend you do the following final step to make access to MiGRIDS easy:

```
ln -s $MIGRIDS $HOME
```

Once you have will have your MiGRIDS available in Windows under your users's `Documents/MiGRIDS` folder and available in your Windows Linux Subsystem as `~/MiGRIDS`.

## Mac Setup

_Work in progress - contact us if you are interested in this_

## Docker Setup

We are working on a docker package for MiGRIDS. Currently we have a working copy for users in Mac/Linux. Check progress on the [Docker Development](Development-Docker) page. 
