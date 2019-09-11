# Projet: MiGRIDS
# Created by: # Created on: 9/10/2019
# Purpose :  qdateFromString
import datetime

def qdateFromString(strDate):
    if type(strDate) == str:
        realDate = datetime.datetime.strptime(strDate, '%Y-%m-%d')
    elif type(strDate) == list:
        realDate = datetime.datetime.strptime(strDate[0], '%Y-%m-%d')
    else:
        realDate = datetime.datetime.today()
    return realDate