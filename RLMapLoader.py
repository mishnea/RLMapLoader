from collections import OrderedDict
from functools import partial
import json
from pathlib import Path
from shutil import copyfile
import tkinter as tk
import tkinter.messagebox as msg

from PIL import Image, ImageTk, ImageDraw, ImageFont


def getfilename(files, ext):
    # get name of first file ending in ext if one exists, else None
    for s in files:
        if s[-len(ext):] == ext:
            return s
    return None


def getdirs():
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
    dirs_dict = {
        "MODS_DIR": mods if mods is not None else MODS_DIR,
        "WORKSHOP_DIR": workshop if workshop is not None else WORKSHOP_DIR,
    }

    with open("dirs.json", "w") as f:
        json.dump(dirs_dict, f)


def warnwrap(f):
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
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.mods_dir = tk.StringVar()
        self.mods_dir.set(MODS_DIR)
        self.workshop_dir = tk.StringVar()
        self.workshop_dir.set(WORKSHOP_DIR)
        self.wkfiles = self.getwkfiles()
        self.modfiles = {}
        self.frames = {}
        self.widgets = {}
        self._initwidgets()

    @staticmethod
    def checkdir(widget, *args):
        try:
            exists = Path(widget.get()).is_dir()
        except OSError:
            exists = False
        if exists:
            widget.config(fg="Black")
        else:
            widget.config(fg="Red")

    def copytolabs(self):
        if not self.widgets["lb_wkfiles"].curselection():
            msg.showerror("Can't activate", "No map selected")
            return
        index = self.widgets["lb_wkfiles"].curselection()[0]
        name, src = list(self.wkfiles.items())[index]
        dest = Path(self.mods_dir.get())
        if dest.is_dir():
            if dest.name != "mods":
                msg.showerror("Invalid path", "Mods path must lead to a folder called 'mods'")
                return
            copyfile(
                src,
                dest.joinpath("Labs_Underpass_P.upk")
            )
            msg.showinfo("Copied!", "Map successfully copied to mods")
            return
        msg.showerror("Invalid path", "Mods path given is not a real directory")

    def deleteunderpass(self):
        path = Path(self.mods_dir.get())
        up_path = path.joinpath("Labs_Underpass_P.upk")
        if path.exists():
            if path.name != "mods":
                msg.showerror("Invalid path", "Mods path must lead to a folder called 'mods'")
                return
            if up_path.exists():
                up_path.unlink()
                msg.showinfo("Restored", "Restored Underpass")
                return
            msg.showinfo("Already restored", "Already restored Underpass")
            return
        msg.showinfo("Invalid path", "Mods path given is not a real directory")

    def getwkfiles(self):
        path = Path(self.workshop_dir.get())
        try:
            udks = OrderedDict((p.name, p) for p in sorted(path.glob("*/*.udk"), key=lambda p: p.name.lower()))
        except OSError:
            return {}
        return udks

    def fillwslist(self, *args):
        self.wkfiles = self.getwkfiles()
        widget = self.widgets["lb_wkfiles"]
        widget.delete(0, tk.END)
        widget.insert(tk.END, *self.wkfiles.keys())

    def savedirs(self, *args):
        savedirs(
            self.mods_dir.get(),
            self.workshop_dir.get(),
        )

    def setdefaults(self, *args):
        self.mods_dir.set(default_dirs["MODS_DIR"])
        self.workshop_dir.set(default_dirs["WORKSHOP_DIR"])

    def makemods(self, *args):
        path = Path(self.mods_dir.get())
        if path.name != "CookedPCConsole":
            msg.showerror(
                "Can't create folder",
                "Can't create mods folder. Must be located within \\CookedPCConsole"
            )
            return
        modspath = Path(path, "mods")
        try:
            modspath.mkdir()
            print("mods directory created")
            self.mods_dir.set(
                str(modspath)
            )
        except FileNotFoundError as exception:
            msg.showerror("No such directory", exception)
        except FileExistsError:
            msg.showinfo("Already exists", "Mods folder already exists")
            self.mods_dir.set(
                str(modspath)
            )

    def _initwidgets(self):
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
        widget.grid(row=1, column=2, rowspan=2, sticky="ns")
        self.widgets["s_wkfiles"] = widget
        widget = tk.Listbox(
            frame,
            width=30,
            selectmode=tk.SINGLE,
            yscrollcommand=self.widgets["s_wkfiles"].set,
        )
        self.widgets["s_wkfiles"].config(command=widget.yview)
        widget.insert(tk.END, *self.wkfiles.keys())
        widget.grid(row=1, column=1, rowspan=2)
        self.widgets["lb_wkfiles"] = widget

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


def start():
    getdirs()
    root = tk.Tk()
    root.title("RLMapLoader")
    # Catch to avoid being garbage collected
    app = MainApp(root) # noqa
    root.mainloop()


if __name__ == "__main__":
    start()
