# Introduction
All component features relevant to the model and analysis are collected in **descriptor** files. These files are all in XML-format with a minimum of nested tags. That is, the generally preferred way of approaching placement of single-value information is in `value`-attributes of appropriately named tags. Where applicable a `unit`-attributed should also carry the units of the associated `value`-attribute. 

Where tuples of triples are concerned, each member of the multiple shall be assigned a dedicated tag, again with `value` and `unit` attribute as needed. 

The entity-relational-diagram below gives and overview of tags and inheritance.

![ERD of Descriptor files](/acep-uaf/MiGRIDS/blob/master/MiGRIDS/Resources/documentationImages/ERD%20for%20GBSTool%20Component%20Descriptors.png)

The following lists and links the available **descriptor** files.

## Interfaces

### `componentDescriptorInterface.xml`
The root interface for all components is described in [`componentDescriptorInterface.xml`](componentDescriptorInterface.xml). 

## Implementations
The following lists, in alphabetical order, implementations of the root interface. Generally, a generic implementation for a particular component exists. Note though that for specific model runs, it is desirable to update these generic descriptors as much as possible with specifics. 

### `controlledLoadDescriptor.xml` : Controlled Load
The [`controlledLoadDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/controlledLoadDescriptor.xml-:-Controlled-Load) file implements a generic controlled load. 

### `eesDescriptor.xml` : Electrical Energy Storage System 
The [`eesDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/eesDescriptor.xml-:-Electrical-Energy-Storage-System) file implements a generic electrical energy storage system.

### `esDescriptor.xml` : Energy Storage System 
The [`esDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/esDescriptor.xml-:-Energy-Storage-System) file implements a generic energy storage system. It has two children that are more specific for electrical and thermal energy storage respectively. 

### `genDescriptor.xml` : Diesel Electric Generator
The [`genDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/genDescriptor.xml-:-Diesel-Electric-Generator) file implements a generic diesel electric generator.

### `invDescriptor.xml` : Inverter
The [`invDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/invDescriptor.xml-:-Inverter) file implements a generic inverter. 

### `loadDescriptor.xml` : Generic Load
The [`loadDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/loadDescriptor.xml-:-Generic-Load) file implements a generic non-controlled load. 

### `wtgDescriptor.xml` : Wind Turbine Generator
The [`wtgDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/wtgDescriptor.xml-:-Wind-Turbine-Generator) file implements a generic wind turbine generator.

### `tesDescriptor.xml` : Thermal Energy Storage System
The [`tesDescriptor.xml`](/acep-uaf/MiGRIDS/wiki/tesDescriptor.xml-:-Thermal-Energy-Storage-System) file implements a generic thermal energy storage system.



