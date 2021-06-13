import subprocess
import smtplib
import json
import logging
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
logger = logging.getLogger(__name__)


# def rchop(s, suffix):
#     if suffix and s.endswith(suffix):
#         return s[:-len(suffix)]
#     return s


def get_secrets(root):
    with open(root + "/secrets/secrets.json", "r") as fi:
        secrets = json.load(fi)
    return secrets


def is_hdd_reachable(name):
    assert name in ["hdd", "hdd2"]
    path = "/media/" + name + "/"
    with open(path + "content/XXX-DO-NOT-DELETE/viruscheck.txt", "r") as fi:
        x1 = fi.read().strip()
    with open(path + "content/XXX-DO-NOT-DELETE/viruscheck.csv", "r") as fi:
        x2 = fi.read().strip()
    reachable = (x1 == "TEST" and x2 == "TEST")
    if not reachable:
        raise FileNotFoundError("Unable to read either viruscheck.txt or viruscheck.csv")
    return reachable


def runSystemCommand(cmds):
    logger.info("Starting runcli")
    logger.debug("Commands are:")
    logger.debug(cmds)

    proc = subprocess.run(
        cmds,
        check=False,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE
    )

    logger.debug("Proc results")
    logger.debug(proc)
    return proc


def send_mail(send_to, send_from, pwd, subject, text, files=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = "Barry <{}>".format(send_from)
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(send_from, pwd)
    server.sendmail(send_from, send_to, msg.as_string())
    server.close()


class result(object):
    def __init__(self, success, log, subject):
        assert isinstance(subject, str)
        assert isinstance(success, bool)
        assert isinstance(log, str) or isinstance(log, bytes) or log is None
        if isinstance(log, str):
            log = log.encode("utf-8")
        self.log = log
        self.success = success
        self.subject = subject
