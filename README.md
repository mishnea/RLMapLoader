# RLMapLoader

Utility for easily setting up custom Rocket League maps to host locally.\
**Windows only. Not tested on versions before Windows 10.**

## Intro

RLMapLoader lets you swap between Steam workshop maps in a couple of clicks, skipping the tedium of manually doing it. It also shows a preview image of the selected map if the creator provided one, helping you to decode the cryptic file names.\
RLMapLoader is also designed to work for Epic Games (EG) users, who need to transfer '.udk' files to load custom maps at all.

## Usage

### Steam users

The workshop directory should be the same or similar to the one that appears by default. You will likely only have to change the drive letter.\
The same goes for the mods directory. However, there is no folder called `mods` within `CookedPCConsole` by default. You can either create it manually, or by clicking **Make Mods Folder** when you've set the `CookedPCConsole` directory.\
The default directories can be recovered at any time by clicking **Defaults**.\
Once the directories are correct, the workshop maps should populate a list. You can search for maps using the textbox above the list.
Double click a map or select it from the list and click **Activate** to load it.

### Epic Games users

The workshop directory should be set to any folder containing your custom maps. For users who also have the Steam version of Rocket League, the Steam workshop folder can also still be used.\
The mods directory should be set similarly to the Steam instructions. A default EG directory can be set by clicking on **Options > Epic Games mode**. From there, you likely only need to change the drive letter and/or click **Make Mods Folder**.\
Once the directories are correct, the workshop maps should populate a list. You can search for maps using the textbox above the list.
Double click a map or select it from the list and click **Activate** to load it.

### Launching the selected map

To launch the map that you activated, you must load Underpass in Training, Exhibition or Local Lobby.

### Symbolic link mode

Version 1.1.0 adds the option of creating symbolic links instead of copying files. This is faster and less taxing on your storage device. However, symlink mode requires administrator privileges or for Developer Mode to be enabled in Windows. Symlink mode is therefore not required. To activate symlink mode, click on **Options > Use symlinks**.

## Python Source Setup

### Using virtual environment

1. Download or clone the repository to your desired location.
2. Open PowerShell.
3. `cd` into the RLMapLoader directory.
4. Run the following:
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -m requirements.txt`

This is enough to develop and run RLMapLoader, however it has to be run using a command line. To create a shortcut to run RLMapLoader using the venv interpreter, follow the next steps:

1. Right click in windows explorer or on the desktop, and click **create shortcut**.
2. In the box, type `<your directory>\RLMapLoader\.venv\Scripts\python.exe "<your directory>\RLMapLoader\RLMapLoader.py"`.
3. Click **Next**.
4. Name the shortcut whatever you like, and click **Finish**.
5. Right click the shortcut, and click properties.
6. Change the 'Start in:' field to `<your directory>\RLMapLoader\`.

_Note: if you want to hide the console while running the program, replace `python.exe` in the instructions with `pythonw.exe`._

### Without virtual environment

1. Download or clone the repository to your desired location.
2. Open PowerShell.
3. `cd` into the RLMapLoader directory.
4. Run `pip install -r requirements.txt`.

You should now be able to run RLMapLoader by double clicking 'RLMapLoader.py', or 'RLMapLoader.pyw' to run without showing the console.

## Requirements

### Executable

- Windows 10 (might work on older versions)

### Python

- Windows 10 (might work on older versions)
- Python 3.x (Python 3.8 or higher is reuired for symlinks to work)
- Tkinter
- PIL (`pip install pillow`)
