import core
import logging
logger = logging.getLogger(__name__)


def main(secrets):
    x = core.runSystemCommand(
        ["rclone", "sync", "/media/hdd2/content", "Barry:", "-v", "--stats=10m"]
    )
    return core.result(
        log=x.stdout,
        success=x.returncode == 0,
        subject="Remote Backup"
    )
