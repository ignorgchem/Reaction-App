# Reaction App
A desktop application for chemical reaction calculations built with Python and Tkinter.

Reaction App helps users calculate reagent quantities based on molar ratios, molar masses, and densities. It provides a simple graphical interface for creating reagent tables, performing calculations, saving/loading presets, and automatically retrieving chemical data from PubChem. 
## Motivation
Working in an organic chemistry laboratory often involves performing numerous calculations for series of reactions where only a single parameter (such as the solvent or the reagent ratio) is varied. Such routine work is time-consuming and increases risk of errors.

This program was designed to streamline the process of setting up organic reactions: it automates calculations, allows storage of experimental parameters and maintains a history of reaction condition optimization.

## Features

- 🧪 Create dynamic reagent calculation tables (1-20 substances)
- ⚗️ Calculate:
	- moles
	- mass (g)
	- volume (mL and µL)
	- required reagent quantities based on molar ratios
- 🌐 Automatically fetch from PubChem database:
	- molecular weight
	- density
	- Both IUPAC nomenclature and trivial names are supported
- 📊 Display calculation results in a table
- 💾 Save and load calculation results as `.txt` files
- 📁 Save and restore reagent presets using `.json` files
- 🔄 Import/export multiple reagent column presets


## Technologies

- Python 3
- Tkinter -graphical user interface
- Pandas - data processing and table generation
- Requests - PubChem API communication
- JSON - preset storage
