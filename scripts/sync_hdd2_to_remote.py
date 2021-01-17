import sys
import os
sys.path.insert(0,  os.path.expanduser("~/Barry"))
import core

core.run_and_report(
    ["rclone", "sync", "/media/hdd2/content", "Barry:", "-v", "--stats=10m"],
    "Bi-Weekly Remote Backup",
    core.filemanager()
)
