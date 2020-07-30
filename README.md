# RL-Mod-Setup
Utility for easily setting up custom Rocket League maps to play with friends\
[YouTube Demonstration](https://youtu.be/-tzFten2xvI)

## Intro
The program presents a GUI which allows the user to see all of the '.udk' files within the Steam workshop maps folder for RL ('\Steam\steamapps\workshop\content\252950'). It also allows the user to select the map they want to host locally and copy it to '\CookedPCConsole\mods\Labs_Underpass_P.upk' by clicking 'Activate'. By copying to '\mods', the original Underpass map isn't overwritten, but will still take precedence when loading. The GUI has some extra features for simple user-friendliness, such as popup dialogs to present warnings, errors and info.\
**The program was created specifically for Windows 10 and is not guaranteed to work with any other OS.**

## Usage
### First run
Upon running the first time, the program will create a file called dirs.txt in the current working directory, given it does not already exist. This file contains a json serialized dict holding the paths of the RL workshop maps directory and mods directory. The file will contain the default paths for both dirs as defined in RLModSetup.py, until they are changed by the user.

### Changing dirs
The GUI has two entry fields, labeled 'Workshop dir' and 'Mods dir'. The text in the fields should be paths to '\Steam\steamapps\workshop\content\252950' and 'rocketleague\TAGame\CookedPCConsole\mods' respectively. The former is where the program looks for '.udk's and the latter is where the program copies the selected '.udk' to. Clicking Defaults next to the workshop field sets both fields to their default values, defined in the program. All changes to these fields are saved, so that on running, the last values from the previous session are loaded in.\
*currently any parent directory also works to find the workshop maps, however this is unintentional and may change as searching through all subdirectories can cause the program to lag*

### Swapping maps
Given the directories are valid, selecting the desired '.udk' from the list followed by clicking 'Activate' will copy the file from the workshop folder to the mods folder, as "Labs_Underpass_P.upk". Any existing file with that name is simply overwritten.\
*intend to add a button in future for deleting "Labs_Underpass_P.upk" altogether, allowing the real Underpass to be loaded*
