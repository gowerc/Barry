import sys
import os
from datetime import date
sys.path.insert(0,  os.path.expanduser("~/Barry"))
import core


core.run_and_report(
    [
        "rsync", "-ahv", "--delete", "--backup",
        '--backup-dir=/media/hdd2/backup/backup_{}'.format(date.today()),
        "/media/hdd/content/", "/media/hdd2/content/"
    ],
    "Weekly Backup",
    core.filemanager()
)
