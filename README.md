# RLMapLoader
Utility for easily setting up custom Rocket League maps to host locally.\
[YouTube Demonstration](https://youtu.be/xliaWYAAnXU)

## Intro
The program presents a GUI which allows the user to see all of the '.udk' files within the Steam workshop maps folder for RL ('\Steam\steamapps\workshop\content\252950'). It also allows the user to select the map they want to host locally and copy it to '\CookedPCConsole\mods\Labs_Underpass_P.upk' by clicking 'Activate'. By copying to '\mods', the original Underpass map isn't overwritten, but will still take precedence when loading. The GUI has some extra features for simple user-friendliness, such as popup dialogs to present warnings, errors and info.\
**The program was created specifically for Windows 10 and is not guaranteed to work with any other OS.**

## Setup

The following instructions will work for Windows users only:

1. Make sure you have Python 3.7 or higher installed. Previous Python 3 versions may work, but it is not guaranteed.
2. Download or clone the repository to your desired location.
3. Open PowerShell.
4. Navigate to the RLMapLoader folder on your computer, using `cd <path to folder>`.
5. Run `pip install -r requirements.txt`. (This step will affect your global Python environment; I recommend using a virtual environment, but this makes running the program slightly more complicated.)

You sould now be able to run RLMapLoader by double clicking 'RLMapLoader.py', or 'RLMapLoader.pyw' to run without showing the console.

## Usage

### First run
On running the first time, the program will create a file called dirs.json in the current working directory, given it does not already exist. This file contains dict holding the paths of the RL workshop maps directory and mods directory. The file will contain the default paths for both dirs as defined in RLModSetup.py, until they are changed by the user.

### Changing dirs
The GUI has two entry fields, labeled 'Workshop dir' and 'Mods dir'. The text in the fields should be paths to '\Steam\steamapps\workshop\content\252950' and 'rocketleague\TAGame\CookedPCConsole\mods' respectively. The former is where the program looks for '.udk's and the latter is where the program copies the selected '.udk' to. Clicking Defaults next to the workshop field sets both fields to their default values, defined in the program. All changes to these fields are saved, so that on running, the last values from the previous session are loaded in. The program will only look in an existing file directory, ending in '252950'.

### Swapping maps
Given the directories are valid, selecting the desired '.udk' from the list followed by clicking 'Activate' will copy the file from the workshop folder to the mods folder, as "Labs_Underpass_P.upk". Any existing file with that name is simply overwritten.

### Restoring Underpass
Clicking 'Restore Underpass' will delete the existing 'Labs_Underpass_P.upk' within mods, allowing RL to load Underpass. This is independent of the workshop path but requires the correct mods path.

## Requirements
- Python 3.x (tested on Python 3.7.8 and 3.8.4)
- PIL (`pip install pillow`)
- Windows 10 (may work on other OSs)
