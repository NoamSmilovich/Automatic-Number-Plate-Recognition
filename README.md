# **Automatic Number Plate Recognition**
![anpr](JPGs/anpr.jpg)
## Intro
The project is an automatic number plate recognition program. It is made up of 3 modules:
 1. GUI -- Responsible for the programs interface and essentially is the main module running the program.
 2. LPD -- The module responsible for the license plate detection using image processing techniques.
 3. OCR -- The module which interfaces with an online OCR API.

This repo contains the code files of each of the modules along with license plate samples.

## Objectives
- Get a deeper understanding of image processing with OpenCV
- Experiment with GUI design
- Interface with an online API using Python

## Installation
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
#### Requirements
This program was tested on Windows 10, 64 bit with Python 3.8 installed.
#### Step-by-Step Procedure
In order to set the virtual environment, apriori installation of virtualenv platform is required.
Use the following commands to create a new working virtual environment with all the required dependencies.
```
git clone https://github.com/NoamSmilovich/Automatic-Number-Plate-Recognition.git
cd Automatic-Number-Plate-Recognition
python -m virtualenv .
.\Scripts\activate
pip install -r requirements.txt
GUI.py
```

### Author
* **Noam Smilovich** - *noamsmi123@gmail.com*
