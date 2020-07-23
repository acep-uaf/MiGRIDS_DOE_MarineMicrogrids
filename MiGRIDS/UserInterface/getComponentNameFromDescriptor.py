# Projet: MiGRIDS_V2.0
# Created by: T. Morgan# Created on: 7/21/2020
# Purpose :  getComponentNameFromDescriptor
import os
def getComponentNameFromDescriptor(descriptorFilePath):
    fileName = os.path.basename(descriptorFilePath)
    return fileName.replace('Descriptor.xml', '')