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

# Start a test
# sudo smartctl -t short  -a /dev/sda

# Get test result
# sudo smartctl -l selftest /dev/sda