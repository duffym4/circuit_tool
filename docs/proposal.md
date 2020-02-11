# Project Proposal

### Project Information
* **Project Name:** Python Circuit Analysis Tool
* **Mattermost Channel:** `/circuit-analysis-tool`
* **Contributors:**
   * PM: Martin Duffy `@duffym4`

### Project Overview
The goal of this project is to provide a platform for circuit analysis. Unlike SPICE and its derivatives, this project aims to provide algebraic and symbolic analysis rather than accurate simulation. This will allow for variable components and mathematical representation of outputs over the time or frequency domains.

This will make use of a powerful python library *lcapy* developed at the University of Canterbury NZ which uses sympy to solve linear circuits with nodal analysis.

The front end will use the cross platform, open source graphical toolkit Qt. Below is a preliminary screen shot of the user interface:

![screen capture](circuit.png)


### Technical Information
* **Language:** Python
* **Libraries:**
   * *PyQt5*: cross platform gui
   * *Lcapy*: linear circuit analysis
   * *Matplotlib*: graphing

### Planned Milestones
* **February:**
   - [x] Finish project proposal
   - [x] Basic schematic editing
   - [ ] Solving time constant circuits
* **March:**
   - [ ] Improved user interface
   - [ ] Solving time dependent circuits
      - [ ] Support capacitors and inductors
   - [ ] Saving and loading circuits
   - [ ] Graphing
* **April:**
   - [ ] Solving for the s domain
   - [ ] Support More Components
      - [ ] Op Amps
      - [ ] Dependent Sources
      - [ ] Diodes
   - [ ] Interactive Mode