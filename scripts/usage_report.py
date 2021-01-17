import sys
import os
sys.path.insert(0,  os.path.expanduser("~/Barry"))
import core

core.run_and_report(
    ["df", "-h"],
    "Usage Report",
    core.filemanager()
)
