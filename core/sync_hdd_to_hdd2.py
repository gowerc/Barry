from datetime import date
import core
import logging
logger = logging.getLogger(__name__)


def main(secrets):
    x = core.runSystemCommand(
        [
            "rsync", "-ahv", "--delete", "--backup",
            "--backup-dir=/media/hdd2/backup/backup_{}".format(date.today()),
            "/media/hdd/content/", "/media/hdd2/content/"
         ]
    )
    return core.result(
        log=x.stdout,
        success=x.returncode == 0,
        subject="Local Backup"
    )
