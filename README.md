# Reaction App

A desktop application for chemical reaction calculations built with **Python** and **Tkinter**.

---

Reaction App is a lightweight desktop utility developed to simplify routine calculations in synthetic chemistry laboratories. The application allows chemists to calculate reagent amounts for multi-component reactions based on stoichiometric ratios, molecular weights, densities, and the desired scale of synthesis.

Instead of performing repetitive calculations manually in spreadsheets or on paper, the user enters the reaction parameters once, after which the program automatically calculates all required quantities. The application also supports reagent presets, experiment templates, and automatic retrieval of physicochemical properties from the PubChem database.


---


# Motivation

Working in an organic chemistry laboratory often involves performing numerous calculations for series of reactions where only a single parameter (such as the solvent or the reagent ratio) is varied. Such routine work is time-consuming and increases risk of errors.

This program was designed to streamline the process of setting up organic reactions: it automates calculations, allows storage of experimental parameters and maintains a history of reaction condition optimization.

---

# Features

## Reagent table

- Create reaction tables containing **1-20 reagents**.
- Dynamically add or remove reagent columns.
- Store the following information for every reagent:
    - structural or common (trivial) name;
    - molar ratio;
    - molecular weight;
    - density.

---

## Automatic calculations

The program performs all calculations starting from the amount of the **first reagent**.

For every reagent it automatically calculates:
- required amount (mol);
- mass (g);
- liquid volume (mL);
- liquid volume (µL).

Calculations are performed according to the specified stoichiometric ratios, allowing rapid scaling of reactions without modifying every reagent individually.

---

## PubChem integration

Reaction App can automatically retrieve physicochemical properties directly from the PubChem database.

Supported properties include:
- molecular weight;
- density.

The program supports both:
- IUPAC names;
- common (trivial) names.

If a compound cannot be found (for example, a newly synthesized molecule or an unpublished intermediate), manually entered values are preserved rather than overwritten.

---

## Presets

The application provides several preset systems for simplifying repetitive work.

### Single reagent preset

Save all parameters of an individual reagent into a JSON file and reuse them in future experiments.

Stored parameters include:
- reagent name;
- molar ratio;
- molecular weight;
- density.

---

### Multi-column preset

Store several reagent columns simultaneously.

This feature is particularly useful for:
- catalyst systems;
- solvent mixtures;
- buffer combinations;
- frequently used reaction conditions.

Presets can either:
- restore reagents to their original columns;
- be inserted starting from any user-selected column.

---

## Import and export

Reaction App supports exchanging data between experiments.

Supported formats include:

### TXT

Reaction tables can be exported as tab-separated text files containing all calculated values.

Previously saved tables can later be imported back into the application.

### JSON

Preset files are stored in human-readable JSON format, making them easy to edit, archive, or share.

---

## User interface

The graphical interface is intentionally simple and lightweight.

Features include:
- table generation;
- all major controls;
- automatic window resizing depending on the number of reagents;
- clipboard support;
- contact dialog for reporting issues.

The application does not require command-line interaction and is intended for everyday laboratory use.

---

# Technologies

- **Python 3** - application logic
- **Tkinter** - graphical user interface
- **Pandas** - generation and formatting of calculation tables
- **Requests** - communication with the PubChem REST API
- **JSON** - preset storage
- **Regular Expressions (re)** - parsing physicochemical properties returned by PubChem
    

---

# Typical workflow

1. Create a reagent table.
2. Enter reagent names and stoichiometric ratios.
3. Optionally retrieve molecular weights and densities from PubChem.
4. Specify the amount of the first reagent.
5. Press **Calculate**.
6. Review the generated reaction table.
7. Save the results or create reusable reagent presets.

---

# Intended users

Reaction App is primarily designed for:
- synthetic organic chemists;
- medicinal chemists;
- graduate students;
- undergraduate laboratory researchers;
- research laboratories that routinely prepare reaction optimization series.

Although originally developed for organic synthesis, the program can also be used whenever reagent quantities must be calculated from stoichiometric relationships.
