import logging
import os
import core
import importlib
import tempfile
import sys


def set_logger():
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    set_logger()
    root = os.path.dirname(os.path.realpath(__file__))
    secrets = core.get_secrets(root)
    arg = sys.argv[1]
    try:
        assert core.is_hdd_reachable("hdd") and core.is_hdd_reachable("hdd2")
        module = importlib.import_module("core." + arg)
        results = module.main(secrets)
    except Exception as e:
        results = core.result(
            log=str(e),
            success=False,
            subject=arg
        )

    result_string = "Success" if results.success else "Failure"

    if results.log:
        tf = tempfile.NamedTemporaryFile(suffix='.txt')
        tf.write(results.log)
        tf.seek(0)
        FILES = [tf.name]
    else:
        FILES = []

    core.send_mail(
        send_to=[secrets["emailAddressTo"]],
        send_from=secrets["emailAddressFrom"],
        pwd=secrets["emailPassword"],
        subject=results.subject + " - " + result_string,
        text="Please see attachements for details",
        files=FILES
    )

    if results.log:
        tf.close()
