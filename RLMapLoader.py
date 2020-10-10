from collections import OrderedDict
from functools import partial
import json
from pathlib import Path
from shutil import copyfile
import tkinter as tk
import tkinter.messagebox as msg
import webbrowser

from PIL import Image, ImageTk, ImageDraw, ImageFont


def getdirs():
    """Update MODS_DIR and WORKSHOP_DIR using saved dirs

    Get directories saved in dirs.json if it exists in the correct format, else use defaults and create the file.
    Sets MODS_DIR and WORKSHOP_DIR and has no return value.
    """

    global MODS_DIR
    global WORKSHOP_DIR

    try:
        with open("dirs.json", "r") as f:
            dirs_dict = json.load(f)
            if type(dirs_dict) != dict:
                raise json.JSONDecodeError
    except (json.JSONDecodeError, FileNotFoundError):
        dirs_dict = default_dirs
        savedirs(mods=dirs_dict["MODS_DIR"], workshop=dirs_dict["WORKSHOP_DIR"])

    MODS_DIR = dirs_dict["MODS_DIR"]
    WORKSHOP_DIR = dirs_dict["WORKSHOP_DIR"]


def savedirs(mods=None, workshop=None):
    """Save mods and workshop directories to dirs.json"""

    dirs_dict = {
        "MODS_DIR": mods if mods is not None else MODS_DIR,
        "WORKSHOP_DIR": workshop if workshop is not None else WORKSHOP_DIR,
    }

    with open("dirs.json", "w") as f:
        json.dump(dirs_dict, f)


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


MODS_DIR = ""
WORKSHOP_DIR = ""


default_dirs = {
    "WORKSHOP_DIR": "C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\252950",
    "MODS_DIR": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\rocketleague\\TAGame\\CookedPCConsole\\mods",
}


class MainApp(tk.Frame):
    """Class defining app behaviour. Acts as a tkinter frame."""

    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.mods_dir = tk.StringVar()
        self.mods_dir.set(MODS_DIR)
        self.workshop_dir = tk.StringVar()
        self.workshop_dir.set(WORKSHOP_DIR)
        self.wkfiles = self.getwkfiles()
        # Size for preview image.
        self.img_size = (160, 160)
        # Generate a default image to be used for preview.
        self.img_default = self.gendefaultimg("No preview")
        self.modfiles = {}
        self.frames = {}
        self.widgets = {}
        self._initwidgets()
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
            widget.config(fg="Black")
        else:
            widget.config(fg="Red")

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
        dest = Path(self.mods_dir.get())
        try:
            is_dir = dest.is_dir()
        except OSError:
            is_dir = False
        if is_dir:
            if dest.name.lower() != "mods":
                msg.showerror("Activate", "Invalid path: Mods path must lead to a folder called 'mods'")
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
            udks = OrderedDict((p.name, p) for p in sorted(path.glob("*/*.udk"), key=lambda p: p.name.lower()))
        except OSError:
            return OrderedDict()
        return udks

    def fillwslist(self, *args):
        """Fill listbox with workshop file names."""

        self.wkfiles = self.getwkfiles()
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

    def savedirs(self, *args):
        """Call global savedirs function with the entry widget values."""

        savedirs(
            self.mods_dir.get(),
            self.workshop_dir.get(),
        )

    def setdefaults(self, *args):
        """Set entry widget values to the paths in default_dirs."""

        self.mods_dir.set(default_dirs["MODS_DIR"])
        self.workshop_dir.set(default_dirs["WORKSHOP_DIR"])

    def gendefaultimg(self, text):
        """Generate image to use when no preview image is available.

        Creates a default image to use when no preview image is found in the selected map's folder or none is selected.
        The image has a transparent background and black text specified by 'text'.
        """

        try:
            font = ImageFont.truetype("arial", 20)
        except OSError:
            font = ImageFont.load_default()
        img = Image.new("RGBA", self.img_size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((30, 65), text, (0, 0, 0, 255), font=font)
        return ImageTk.PhotoImage(img)

    def changeimg(self):
        """Change to the preview image for the selected map.

        Changes to the default image if no image is available or no map is selected.
        """

        filetypes = ("*.png", "*.jpg", "*.jpeg", "*.bmp")

        selection = self.getselected()
        if not selection:
            self.image = self.img_default
            self.widgets["l_preview"].configure(image=self.image)
            return
        path = selection[1].parent
        images = []
        for ext in filetypes:
            images.extend(Path(path).glob(ext))
        if images:
            im = Image.open(images[0])
            size = self.img_size
            im.thumbnail(size)
            self.image = ImageTk.PhotoImage(im)
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
            msg.showerror("Make mods folder", "Can't create mods folder. Must be located within \\CookedPCConsole")
            return
        modspath = Path(path, "mods")
        try:
            modspath.mkdir()
            msg.showinfo("Make mods folder", "Successfully created folder. Changed mods dir to new folder.")
            self.mods_dir.set(
                str(modspath)
            )
        except FileNotFoundError:
            msg.showerror("Make mods folder", "Path specified in mods dir is not a real directory")
        except FileExistsError:
            msg.showinfo("Make mods folder", "Mods folder already exists")
            self.mods_dir.set(
                str(modspath)
            )

    def _initwidgets(self):
        """Initialise widgets."""

        self.widgets = {}

        widget = tk.Label(self, text="Workshop dir:")
        widget.grid(row=0, sticky="e")
        self.widgets["l_wkdir"] = widget

        widget = tk.Entry(
            self,
            textvariable=self.workshop_dir,
            width=60,
        )
        self.workshop_dir.trace("w", multi(
            partial(self.checkdir, widget),
            self.savedirs,
            self.fillwslist,
        ))
        widget.grid(row=0, column=1)
        self.checkdir(widget)
        self.widgets["e_wkdir"] = widget

        widget = tk.Label(self, text="Mods dir:")
        widget.grid(row=1, sticky="e")
        self.widgets["l_mdir"] = widget

        widget = tk.Entry(
            self,
            textvariable=self.mods_dir,
            width=60,
        )
        self.mods_dir.trace("w", multi(
            partial(self.checkdir, widget),
            self.savedirs,
        ))
        widget.grid(row=1, column=1)
        self.checkdir(widget)
        self.widgets["e_mdir"] = widget

        widget = tk.Button(
            self,
            text="Defaults",
            command=self.setdefaults
        )
        widget.grid(row=0, column=2, rowspan=1, sticky="we")
        self.widgets["b_defaults"] = widget

        widget = tk.Button(
            self,
            text="Make mods folder",
            command=warnwrap(self.makemods)
        )
        widget.grid(row=1, column=2, rowspan=1)
        self.widgets["b_mkmods"] = widget

        frame = tk.Frame(self)
        frame.grid(row=2, columnspan=3)
        self.frames["middle"] = frame
        widget = tk.Label(frame, text="Workshop Files")
        widget.grid(row=0, column=1)
        self.widgets["l_wkfiles"] = widget
        widget = tk.Scrollbar(frame)
        widget.grid(row=1, column=2, rowspan=3, sticky="ns")
        self.widgets["s_wkfiles"] = widget
        widget = tk.Listbox(
            frame,
            width=30,
            selectmode=tk.SINGLE,
            yscrollcommand=self.widgets["s_wkfiles"].set,
        )
        self.widgets["s_wkfiles"].config(command=widget.yview)
        widget.insert(tk.END, *self.wkfiles.keys())
        widget.grid(row=1, column=1, rowspan=1)
        self.widgets["lb_wkfiles"] = widget

        width, height = self.img_size
        widget = tk.Label(
            frame,
            image=self.img_default,
            width=width,
            height=height
        )
        widget.grid(row=1, column=0, rowspan=1)
        self.widgets["l_preview"] = widget

        frame = tk.Frame(self.frames["middle"])
        frame.grid(row=1, column=3)
        self.frames["middle.right"] = frame

        widget = tk.Button(
            frame,
            text="Activate",
            command=self.copytolabs,
        )
        widget.grid(row=1, column=3, sticky="wes")
        self.widgets["b_tolabs"] = widget

        widget = tk.Button(
            frame,
            text="Restore Underpass",
            command=self.deleteunderpass,
        )
        widget.grid(row=2, column=3, sticky="n")
        self.widgets["b_restore"] = widget

        widget = tk.Button(
            frame,
            text="Open Folder",
            command=self.openfolder,
        )
        widget.grid(row=3, column=3, sticky="wen")
        self.widgets["b_openfolder"] = widget


def start():
    """Start the program."""

    getdirs()
    root = tk.Tk()
    root.title("RLMapLoader")
    root.resizable(False, False)
    # Catch object to avoid garbage collection.
    app = MainApp(root) # noqa
    root.mainloop()


if __name__ == "__main__":
    start()
