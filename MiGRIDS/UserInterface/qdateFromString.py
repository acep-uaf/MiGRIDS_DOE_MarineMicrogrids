# Projet: MiGRIDS
# Created by: # Created on: 9/10/2019
# Purpose :  qdateFromString
import datetime
from PyQt5 import QtCore


def qdateFromString(strDate):
    if (type(strDate) == str) & (strDate != 'None'):
       return QtCore.QDate(asDate(strDate))
    elif type(strDate) == list:
       return QtCore.QDate(asDate(strDate[0]))
    else:
        return QtCore.QDate(datetime.datetime.today())


def asDate(strDate):
    try:
        realDate = datetime.datetime.strptime(strDate, '%Y-%m-%d')
    except ValueError as v:
        try:
            realDate = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return None

    return realDate