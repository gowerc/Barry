import sys
import os
sys.path.insert(0,  os.path.expanduser("~/Barry"))
import core

fm = core.filemanager()
core.sync_github(fm)
