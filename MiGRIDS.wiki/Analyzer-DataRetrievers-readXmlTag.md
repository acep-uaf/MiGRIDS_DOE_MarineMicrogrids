The function `readXmlTag` returns the value from a tag in an XML file. 

# Inputs
**fileName**: The name of the XML file. 

**tag**: The tag to be read. 

**attr**: the tag attribute to be read. 

**fileDir**: is the directory where the file is saved. This can be left empty. 

**returnDType**: This is a string that specifies the datatype to return the value as. It can be 'int', 'float' or ''. If left as '', then the datatype will not be converted. 

# Outputs
**tagValues**: The value of XML tag. 