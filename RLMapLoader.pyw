# Used for building .exe to avoid showing console

import RLMapLoader as main
import sys

logfile = open(main.APPDATA_FOLDER.joinpath("log.txt"), "w")
sys.stdout = logfile
sys.stderr = logfile

main.start()
