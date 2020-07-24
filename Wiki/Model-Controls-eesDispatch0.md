# Introduction
[eesDispatch0](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Model/Controls/eesDispatch0.py) proportionally charges and discharges each [EES](ElectricalEnergyStorage-Class) based on their maximum power they are able to be charged or discharged by at that simulation step. The maximum power is calculated by each `EES` and takes into account their state of charge. 
