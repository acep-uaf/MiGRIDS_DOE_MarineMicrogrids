# MiGRIDS 
Welcome to **MiGRIDS**!  MiGRIDS stands for **Mi**cro **G**rid **R**enewable **I**ntegration **D**ispatch and **S**izing. 

MiGRIDS is a software that models islanded microgrid power systems with different controls and components. For example, using load and resource data from a microgrid, you could model it with additional wind turbines, battery etc. You could also try out different dispatch schemes to see which one worked best.
 
MiGRIDS is designed to help optimize the size and dispatch of grid components in a microgrid. While a grid connect feature is expected to be added in the future, islanded operation is the focus. Note that this is a basic implementation and more features and functionality (such as a GUI) are coming!

MiGRIDS runs time-step energy balance simulations for different grid components and controls. In smaller microgrid environments, dispatch decisions are being made on the order of seconds. In order to fully capture their effect, this tool lets you run simulations on the order of seconds. The end result is a more realistic representation of what can be achieved by integrating different components and control strategies in a grid.

### Installing and Running MiGRIDS

The [MiGRIDS/wiki](https://github.com/acep-uaf/MiGRIDS/wiki) is the primary
location for documentation of the model, installation instructions, and
description of the software packages and project tutorials.

* [MiGRIDS Install Instructions](https://github.com/acep-uaf/MiGRIDS/wiki/MiGRIDS-Installation) 
* [MiGRIDS Documentation](https://github.com/acep-uaf/MiGRIDS/wiki/MiGRIDS-Tool-Home)
* [MiGRIDS Simulation Instructions](https://docs.google.com/document/d/1qX6ELLBZj3Jf9jWXH8BFMGMduzkq6oYsOUMRN03o7E0/edit)


## MiGRIDS history

MiGRIDS was developed by a research team at the University of Alaska Fairbanks [Alaska Center for
Energy and Power (ACEP)](https://acep.uaf.edu). MiGRIDS was originally developed
as a set of tools under the name Grid Bridging System Tool (GBSTool) by Jeremy VanderMeer and [Marc Mueller-Stoffles](https://github.com/mmuellerstoffels). The GBSTool was then expanded and updated into the MiGRIDS package.

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).

## Authors & Contributors

- Jeremy Vandermeer - [@jbvandermeer](https://github.com/jbvandermeer) 
  - Lead Developer at ACEP
- Marc Mueller-Stoffles - [@mmuellerstoffles](https://github.com/mmullerstoffles)
  - Original Co-Developer 
- Tawna Morgan - [@tawnamorgan](https://github.com/tawnamorgan)
- Dayne Broderson - [@dayne](https://github.com/dayne)
