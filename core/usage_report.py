import core
import logging
logger = logging.getLogger(__name__)


def main(secrets):
    x = core.runSystemCommand(["df", "-h"])
    return core.result(
        log=x.stdout,
        success=x.returncode == 0,
        subject="Usage Report"
    )
