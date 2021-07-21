# PDEA
Pdf table data extraction and analysis repository

## Note: The Notebooks are just for testing snippets and should not be considered as final code. Alwayes restart the kernel and clear the output before pushing the notebook! 

## Contributors:
* Curtin Institute for Computation (CIC)
  * Foad Farivar (foad.farivar@curtin.edu.au)
  * Daniel Marrable (D.Marrable@curtin.edu.au)
 
* School of Management and Marketing 
  * Ramon Wenel (ramon.wenzel@curtin.edu.au)

# Running the notebooks and python scripts contained in this repository
## Anaconda Navigator
Anaconda Navigator makes it easier to manage the installation of python, launch applications and manage packages and environments. To install Anaconda Navigator:

On Windows:
1. Open https://www.anaconda.com/distribution/#download-section with your web browser.
2. Download the Anaconda for Windows installer with Python 3.8. (If you are not sure which version to choose, you probably want the 64-bit Graphical Installer Anaconda3-...-Windows-x86_64.exe)
3. Install Python 3 by running the Anaconda Installer, using all of the defaults for installation except make sure to check Add Anaconda to my PATH environment variable.

On a Mac:
1. Open https://www.anaconda.com/distribution/#download-section with your web browser.
2. Download the Anaconda Installer with Python 3.8 for macOS (you can either use the Graphical or the Command Line Installer).
3. Install Python 3 by running the Anaconda Installer using all of the defaults for installation.

On Linux:
1. Open https://www.anaconda.com/distribution/#download-section with your web browser.
2. Download the Anaconda Installer with Python 3.8 for Linux.
(The installation requires using the shell. If you aren't comfortable doing the installation yourself stop here and request help at the workshop.)
3. Open a terminal window and navigate to the directory where the executable is downloaded (e.g., `cd ~/Downloads`).
4. Type
```bash Anaconda3-```
and then press ```Tab``` to autocomplete the full file name. The name of file you just downloaded should appear.
5. Press ```Enter```. You will follow the text-only prompts. To move through the text, press ```Spacebar```. Type yes and press enter to approve the license. Press ```Enter``` to approve the default location for the files. Type yes and press ```Enter``` to prepend Anaconda to your PATH (this makes the Anaconda distribution the default Python).
6. Close the terminal window.

### Setting up and updating a conda environment

Anaconda includes an environment manager called conda. Environments allow you to have multiple sets of Python packages installed at the same time, making reproducibility and upgrades easier. You can create, export, list, remove, and update environments that have different versions of Python and/or packages installed in them.

You can create a conda environment for this project using the provided environment.yml file. The python version and all needed packages are listed in the environment.yml file.

**Using the command line**

On Mac or Linux, open your terminal, on Windows, open the Anaconda Prompt terminal app.

Now navigate to this repository directory in the terminal. For example, if you installed the PDEA repository on your Desktop, you could type the following.

On a Mac/Linux:
```
% cd Desktop/PDEA/
```
On Windows:
```
% cd Desktop\PDEA\
```
And finally, on any platform, to install and activate the PDEA environment, type:
```
% conda env create --file environment.yml
% conda activate PDEA
```
To deactivate the environemnt, tyoe:
```
% conda deactivate PDEA
```

Note, you will need conda version 4.6 and later. If you need to update your version use 
```
% conda update conda
```

**Update environment**

To update your environment as new packages are added to the environment.yml file, type:
```
% conda activate PDEA
% conda env update --file environment.yml
```

### Importing the PDEA environment into Anaconda for the first time
After creating the PDEA environment, open Anaconda Navigator and follow these steps:

1. Click on the Environment tab in the left-hand menu
2, Choose the Import button at the bottom of the page
3. In the new dialog window click on the folder icon and search for the environment.yml file in the workshop material you downloaded.
4. This should populate the Name, Location and Specification File fields in the dialog box.
5. Click Import 
6. Conda is now installing the required version of Python and packages

### Using jupyter notebook to run the notebooks through Anaconda Navigator
Launch a jupyter notebook by selecting the environment and clicking the play button and choosing “Open with Jupyter Notebook”

### Using jupyter notebook to run the notebooks from the command line
On Mac or Linux, open your terminal, on Windows, open the Anaconda Prompt terminal app and navigate to this repository directory in the terminal. Activate the environment and start jupyter notebook by typing:

```
% conda activate PDEA
% jupyter notebook
```

## Running python scripts from the command line
On Mac or Linux, open your terminal, on Windows, open the Anaconda Prompt terminal app and activate the PDEA environment.
Create a PDFs directory and copy all the pdf files into this directory. 
If you are running the script multiple times make sure you save the produced **Processed.xlsx** file

To run the stand alone python scripts that end in .py type:
```
% python ./Pdf_table_extr.py
```

## Pushing changes to GitHub
If you have write permissions to the PDEA GitHub repo and wish to commit and push your jupter notebooks, always remember to select **Kernal** and click **Restart Kernal and clear output** BEFORE SAVING AND PUSHING THE CHANGES to GitHub.


*conda environment notes adapted from the astropy workshop [repo](https://github.com/astropy/astropy-workshop).

*jupyter lab and plotly instructions: https://plotly.com/python/getting-started/
