from collections import OrderedDict
from configparser import ConfigParser
from functools import partial
from itertools import chain
import os
from pathlib import Path
import re
from shutil import copyfile
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as msg
import webbrowser

from PIL import Image, ImageTk, ImageDraw, ImageFont

from scraper import WorkshopItem, ItemNotFoundError


def warnwrap(f):
    """Wrap a widget callback to raise a warning.

    Raises a warning messagebox before calling the function passed to 'f'.
    Only calls the function is the user responds with 'ok'.
    """

    def func(*args, **kwargs):
        ans = msg.showwarning(
            title="Create folder",
            message="Do you want to continue?",
            type=msg.OKCANCEL,
            default=msg.CANCEL,
        )
        if ans == "ok":
            f(*args, **kwargs)
    return func


def multi(*funcs):
    """Pass many functions as one widget callback.

    Takes any number of functions. Returns a function which calls all of the wrapped functions with the same args.
    Returns a list of the return values.
    """

    def many_func(*args, **kwargs):
        return [f(*args, **kwargs) for f in funcs]

    return many_func


HELP_URL = "https://github.com/mishnea/RLMapLoader#usage"

# Appdata Folders
APPDATA_FOLDER = Path(os.getenv("appdata"), "RLMapLoader")
APPDATA_FOLDER.mkdir(exist_ok=True)

CACHE_FOLDER = APPDATA_FOLDER.joinpath("imgcache")
CACHE_FOLDER.mkdir(exist_ok=True)


class MainApp(tk.Tk):
    """Class defining app behaviour. Acts as a tkinter frame."""

    def __init__(self):
        super().__init__()

        self.title("RLMapLoader")
        self.iconbitmap("icon.ico")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.onclose)

        self.loadcfg()
        self.search = tk.StringVar(value="")
        self.use_symlinks = tk.IntVar(value=self.usercfg.getint("UseSymlinks"))
        self.eg_mode = tk.IntVar(value=self.usercfg.getint("EGMode"))
        self.workshop_dir = tk.StringVar(value=self.usercfg["WorkshopDir"])
        if self.eg_mode.get():
            self.mods_dir = tk.StringVar(value=self.usercfg["EGModsDir"])
        else:
            self.mods_dir = tk.StringVar(value=self.usercfg["ModsDir"])
        self.wkfiles = self.getwkfiles()
        # Size for preview image.
        self.img_size = (240, 158)
        # Get a default image to be used for preview.
        self.img_default = self.getdefaultimg("default.png", alt_text="No preview")
        self.modfiles = {}
        self.frames = {}
        self.widgets = {}
        self._initwidgets()
        self._initmenu()
        # Start preview update on a timer.
        self.updateimg()

    @staticmethod
    def checkdir(widget, *args):
        """Check if the value of a widget is a path to an existing directory.

        Applies formatting to the widget's text based on the result.
        """

        try:
            is_dir = Path(widget.get()).is_dir()
        except OSError:
            is_dir = False
        if is_dir:
            widget.config(style="TEntry")
        else:
            widget.config(style="R.TEntry")

    def onclose(self):
        self.savecfg()
        self.destroy()

    def loadcfg(self):
        filename = "settings.ini"
        path = APPDATA_FOLDER.joinpath(filename)
        self.settings = ConfigParser()
        if path.exists():
            self.settings.read(path)
        else:
            self.settings["DEFAULT"] = {
                "workshopdir": "C:/Program Files (x86)/Steam/steamapps/workshop/content/252950",
                "modsdir": "C:/Program Files (x86)/Steam/steamapps/common/rocketleague/TAGame/CookedPCConsole/mods",
                "egmodsdir": "C:/Program Files/Epic Games/rocketleague/TAGame/CookedPCConsole/mods",
                "egmode": 0,
                "usesymlinks": 0,
            }
            self.settings["user"] = {}
        self.usercfg = self.settings["user"]

    def savecfg(self):
        self.usercfg["WorkshopDir"] = self.workshop_dir.get()
        if self.eg_mode.get():
            self.usercfg["EGModsDir"] = self.mods_dir.get()
        else:
            self.usercfg["ModsDir"] = self.mods_dir.get()
        self.usercfg["EGMode"] = str(self.eg_mode.get())
        self.usercfg["UseSymlinks"] = str(self.use_symlinks.get())
        filename = "settings.ini"
        path = APPDATA_FOLDER.joinpath(filename)
        with open(path, "w") as config_file:
            self.settings.write(config_file)

    def changemode(self, *args, **kwargs):
        self.widgets["e_mdir"].delete(0, tk.END)
        if self.eg_mode.get():
            self.widgets["e_mdir"].insert(0, self.usercfg["EGModsDir"])
        else:
            self.widgets["e_mdir"].insert(0, self.usercfg["ModsDir"])

    def getselected(self):
        """Return the name and path of the selected map.

        Returns a tuple containing the current selection's items, or an empty tuple if nothing is selected
        """

        if not self.widgets["lb_wkfiles"].curselection():
            return ()
        index = self.widgets["lb_wkfiles"].curselection()[0]
        return list(self.wkfiles.items())[index]

    def copytolabs(self):
        """Copy the selected map to the mods folder

        Tries to copy the selected '.udk' file to the mods folder. Shows a messagebox on success or failure.
        """

        selection = self.getselected()
        if not selection:
            msg.showerror("Activate", "Cannot activate: No map selected")
            return
        name, src = selection
        if not Path(src).is_file():
            msg.showerror("Activate", "Cannot activate: File not found")
            return
        dest = Path(self.mods_dir.get())
        try:
            is_dir = dest.is_dir()
        except OSError:
            is_dir = False
        if is_dir:
            if dest.name.lower() != "mods":
                msg.showerror("Activate", "Invalid path: Mods path must lead to a folder called 'mods'")
                return
            up_path = Path(dest.joinpath("Labs_Underpass_P.upk"))
            if up_path.exists():
                up_path.unlink()
            if self.use_symlinks.get():
                try:
                    up_path.symlink_to(src)
                except OSError as e:
                    msg.showerror("Activate", f"Couldn't create symlink. Full Python exception:\n{repr(e)}")
                    return
                msg.showinfo("Activate", "Symlink successfully created in mods")
                return
            copyfile(
                src,
                dest.joinpath("Labs_Underpass_P.upk")
            )
            msg.showinfo("Activate", "Map successfully copied to mods")
            return
        msg.showerror("Activate", "Invalid path: Mods path given is not a real directory")

    def deleteunderpass(self):
        """Delete 'Underpass' from the mods folder.

        Tries to delete 'Labs_Underpass_P.upk' from the mods folder.
        Displays a messagebox with the outcome.
        """

        path = Path(self.mods_dir.get())
        up_path = path.joinpath("Labs_Underpass_P.upk")
        try:
            is_dir = path.is_dir()
        except OSError:
            is_dir = False
        if is_dir:
            if path.name.lower() != "mods":
                msg.showerror("Restore Underpass", "Invalid path: Mods path must lead to a folder called 'mods'")
                return
            if up_path.exists():
                up_path.unlink()
                msg.showinfo("Restore Underpass", "Successfully restored Underpass")
                return
            msg.showinfo("Restore Underpass", "Already restored Underpass")
            return
        msg.showerror("Restore Underpass", "Invalid path: Mods path given is not a real directory")

    def getwkfiles(self):
        """Return an OrderedDict containing name-path pairs of workshop files."""

        path = Path(self.workshop_dir.get())
        try:
            paths = sorted(chain(path.glob("*/*.udk"), path.glob("*.udk")), key=lambda p: p.name.lower())
        except OSError:
            return OrderedDict()
        udks = OrderedDict((p.name, p) for p in paths)
        return udks

    def fillwslist(self, *args):
        """Fill listbox with workshop file names."""

        pattern = f".*{re.escape(self.search.get())}.*"
        self.wkfiles = {k: v for k, v in self.getwkfiles().items() if re.match(pattern, k, re.IGNORECASE)}

        widget = self.widgets["lb_wkfiles"]
        widget.delete(0, tk.END)
        widget.insert(tk.END, *self.wkfiles.keys())

    def openfolder(self, *args):
        """Open selected folder in File Explorer."""

        try:
            name, src = self.getselected()
            path = src.parent
        except ValueError:
            path = self.workshop_dir.get()
        try:
            is_dir = Path(path).is_dir()
        except OSError:
            is_dir = False
        if is_dir:
            webbrowser.open(path)
        else:
            msg.showerror("Open Folder", f"Can't open folder. \"{path}\" is not a valid directory.")

    def setdefaults(self, *args):
        """Set entry widget values to the paths in default_dirs."""

        self.widgets["e_wkdir"].delete(0, tk.END)
        self.widgets["e_mdir"].delete(0, tk.END)

        if self.eg_mode.get():
            self.widgets["e_mdir"].insert(0, self.settings["DEFAULT"]["EGModsDir"])
        else:
            self.widgets["e_mdir"].insert(0, self.settings["DEFAULT"]["ModsDir"])
        self.widgets["e_wkdir"].insert(0, self.settings["DEFAULT"]["WorkshopDir"])

    def getdefaultimg(self, filename, alt_text):
        """Gets an image to use when no preview image is available.

        Gets a default image to use when no preview image is found in the selected map's folder or none is selected.
        filename - name of default image file to get
        alt_text - text to use when generating image if the file is not found
        """

        # Get default image from file
        path = Path(filename)
        if path.is_file():
            im = Image.open(path)
            im.thumbnail(self.img_size)
            return ImageTk.PhotoImage(im)

        # Generate a default image from alt_text
        try:
            font = ImageFont.truetype("arial", 20)
        except OSError:
            font = ImageFont.load_default()
        img = Image.new("RGBA", self.img_size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((70, 66), alt_text, (0, 0, 0, 255), font=font)
        return ImageTk.PhotoImage(img)

    def changeimg(self):
        """Change to the preview image for the selected map.

        Changes to the default image if no image is available or no map is selected.
        """

        filetypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp")

        selection = self.getselected()
        # Load default.png if it exists, else list is empty.
        images = list()
        if selection:
            path = selection[1].parent
            for ext in filetypes:
                images.extend(Path(path).glob(ext))
            size = self.img_size
            if images:
                im = Image.open(images[-1])
                im.thumbnail(size)
                self.image = ImageTk.PhotoImage(im)
            elif CACHE_FOLDER.joinpath(path.name + ".png").is_file():
                im = Image.open(CACHE_FOLDER.joinpath(path.name + ".png"))
                self.image = ImageTk.PhotoImage(im)
            else:
                try:
                    workshop_id = path.name
                    im = WorkshopItem(workshop_id).get_img()
                    im.thumbnail(size)
                    im.save(CACHE_FOLDER.joinpath(workshop_id + ".png"), format="PNG")
                    self.image = ImageTk.PhotoImage(im)
                except ItemNotFoundError:
                    self.image = self.img_default
        else:
            self.image = self.img_default
        self.widgets["l_preview"].configure(image=self.image)

    def updateimg(self, previous=None, delay=100):
        """Call the changeimg method if the map selection has changed.

        Checks whether the selection has changed periodically. The period is specified by 'delay', in milliseconds.
        Achieved by the function calling itself on a timer.
        """

        selected = self.getselected() or (None,)
        name = selected[0]
        if name != previous:
            self.changeimg()
        self.after(delay, lambda: self.updateimg(previous=name))

    def makemods(self, *args):
        """Tries to make a folder called 'mods' in the current mods directory.

        Makes a new folder called 'mods' in the specified mods directory if it doesn't already exist.
        The directory must exist and be called 'CookedPCConsole'.
        Displays a messagebox with the outcome.
        """

        path = Path(self.mods_dir.get())
        if path.name != "CookedPCConsole":
            path = path.parent
            if path.name != "CookedPCConsole":
                msg.showerror("Make mods folder", "Can't create mods folder. Must be located within \\CookedPCConsole")
                return
        modspath = Path(path, "mods")
        try:
            modspath.mkdir()
            msg.showinfo("Make mods folder", "Successfully created folder. Changed mods dir to new folder.")
            self.widgets["e_mdir"].delete(0, tk.END)
            self.widgets["e_mdir"].insert(0, str(modspath))
        except FileNotFoundError:
            msg.showerror("Make mods folder", "Path specified in mods dir is not a real directory")
        except FileExistsError:
            msg.showinfo("Make mods folder", "Mods folder already exists")
            self.widgets["e_mdir"].delete(0, tk.END)
            self.widgets["e_mdir"].insert(0, str(modspath))

    def browsewkdir(self):
        path = filedialog.askdirectory(title="Select Workshop Folder")
        if not path:
            return
        self.widgets["e_wkdir"].delete(0, tk.END)
        self.widgets["e_wkdir"].insert(0, path)

    def browsemdir(self):
        path = filedialog.askdirectory(title="Select Mods Folder")
        if not path:
            return
        self.widgets["e_mdir"].delete(0, tk.END)
        self.widgets["e_mdir"].insert(0, path)

    def symlinkwarning(self):
        if self.use_symlinks.get():
            msg.showwarning(
                "Use Symlinks",
                "Symlinks will only be created if RLMapLoader is run with admin privileges, or Developer Mode is "
                "enabled in Windows. Only use this if you know what you're doing."
            )

    def _initwidgets(self):
        """Initialise widgets."""

        self.frames["main"] = ttk.Frame(self)
        self.frames["main"].pack()

        self.frames["main"].config(pad=4)

        self.widgets = {}

        self.widgets["l_wkdir"] = ttk.Label(self.frames["main"], text="Workshop dir:")
        self.widgets["l_wkdir"].grid(row=0, sticky="e")

        ttk.Style().configure("R.TEntry", foreground="#f00")
        self.widgets["e_wkdir"] = ttk.Entry(
            self.frames["main"],
            textvariable=self.workshop_dir,
            width=60
        )
        self.workshop_dir.trace("w", multi(
            partial(self.checkdir, self.widgets["e_wkdir"]),
            self.fillwslist,
        ))
        self.widgets["e_wkdir"].grid(row=0, column=1)
        self.checkdir(self.widgets["e_wkdir"])

        self.widgets["l_mdir"] = ttk.Label(self.frames["main"], text="Mods dir:")
        self.widgets["l_mdir"].grid(row=1, sticky="e")

        self.widgets["e_mdir"] = ttk.Entry(
            self.frames["main"],
            textvariable=self.mods_dir,
            width=60
        )
        self.mods_dir.trace("w", partial(self.checkdir, self.widgets["e_mdir"]))
        self.widgets["e_mdir"].grid(row=1, column=1)
        self.checkdir(self.widgets["e_mdir"])

        self.widgets["b_wkbrowse"] = ttk.Button(
            self.frames["main"],
            text="...",
            width=2,
            command=self.browsewkdir
        )
        self.widgets["b_wkbrowse"].grid(row=0, column=2)

        self.widgets["b_mbrowse"] = ttk.Button(
            self.frames["main"],
            text="...",
            width=2,
            command=self.browsemdir
        )
        self.widgets["b_mbrowse"].grid(row=1, column=2)

        self.widgets["b_defaults"] = ttk.Button(
            self.frames["main"],
            text="Defaults",
            command=self.setdefaults
        )
        self.widgets["b_defaults"].grid(row=0, column=3, rowspan=1, sticky="we")

        self.widgets["b_mkmods"] = ttk.Button(
            self.frames["main"],
            text="Make Mods Folder",
            command=warnwrap(self.makemods)
        )
        self.widgets["b_mkmods"].grid(row=1, column=3, rowspan=1)

        self.frames["middle"] = ttk.Frame(self.frames["main"])
        self.frames["middle"].grid(row=2, columnspan=4)

        self.widgets["l_wkfiles"] = ttk.Label(self.frames["middle"], text="Workshop Files")
        self.widgets["l_wkfiles"].grid(row=0, column=1)

        self.widgets["e_wksearch"] = ttk.Entry(
            self.frames["middle"],
            textvariable=self.search,
        )
        self.widgets["e_wksearch"].grid(row=1, column=1, sticky="we", pady=1)
        self.search.trace("w", self.fillwslist)
        self.widgets["e_wksearch"].bind(
            "<FocusIn>",
            lambda event: event.widget.delete(0, tk.END),
        )

        self.widgets["s_wkfiles"] = ttk.Scrollbar(self.frames["middle"])
        self.widgets["s_wkfiles"].grid(row=2, column=2, rowspan=3, sticky="ns")

        self.widgets["lb_wkfiles"] = tk.Listbox(
            self.frames["middle"],
            height=9,
            width=30,
            highlightthickness=-1,
            activestyle=tk.NONE,
            relief=tk.SOLID,
            selectmode=tk.SINGLE,
            yscrollcommand=self.widgets["s_wkfiles"].set,
            cursor="hand2"
        )
        self.widgets["s_wkfiles"].config(command=self.widgets["lb_wkfiles"].yview)
        self.widgets["lb_wkfiles"].insert(tk.END, *self.wkfiles.keys())
        self.widgets["lb_wkfiles"].grid(row=2, column=1, rowspan=1)
        self.widgets["lb_wkfiles"].bind("<Double-Button-1>", lambda event: self.copytolabs())

        width, height = self.img_size
        self.widgets["l_preview"] = tk.Label(
            self.frames["middle"],
            image=None,
            width=width,
            height=height,
            bd=2,
            padx=5
        )
        self.changeimg()
        self.widgets["l_preview"].grid(row=1, column=0, rowspan=2)

        self.frames["middle.right"] = ttk.Frame(self.frames["middle"])
        self.frames["middle.right"].grid(row=1, column=3, rowspan=2)

        self.widgets["b_tolabs"] = ttk.Button(
            self.frames["middle.right"],
            text="Activate",
            command=self.copytolabs,
        )
        self.widgets["b_tolabs"].grid(row=1, column=3, sticky="wes")

        self.widgets["b_restore"] = ttk.Button(
            self.frames["middle.right"],
            text="Restore Underpass",
            command=self.deleteunderpass,
        )
        self.widgets["b_restore"].grid(row=2, column=3, sticky="n")

        self.widgets["b_openfolder"] = ttk.Button(
            self.frames["middle.right"],
            text="Open Folder",
            command=self.openfolder,
        )
        self.widgets["b_openfolder"].grid(row=3, column=3, sticky="wen")

    def _initmenu(self):
        self.topmenu = tk.Menu(self)

        self.helpmenu = tk.Menu(self, tearoff=0)
        self.helpmenu.add_command(
            label="Usage instructions",
            command=lambda: webbrowser.open(HELP_URL),
        )

        self.optionsmenu = tk.Menu(self, tearoff=0)
        self.optionsmenu.add_checkbutton(
            label="Epic Games mode",
            var=self.eg_mode,
            offvalue=0,
            onvalue=1,
            command=self.changemode,
        )
        self.optionsmenu.add_checkbutton(
            label="Use symlinks",
            var=self.use_symlinks,
            offvalue=0,
            onvalue=1,
            command=self.symlinkwarning,
        )
        self.optionsmenu.add_separator()
        self.optionsmenu.add_command(
            label="Exit",
            command=self.onclose,
        )

        self.topmenu.add_cascade(label="Options", menu=self.optionsmenu)
        self.topmenu.add_cascade(label="Help", menu=self.helpmenu)

        self.config(menu=self.topmenu)


def start():
    """Start the program."""

    # Catch object to avoid garbage collection.
    app = MainApp() # noqa
    app.mainloop()


if __name__ == "__main__":
    start()
