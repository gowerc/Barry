import subprocess
import smtplib
import os
import requests
import logging
import sys
import json
import pathlib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate



def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

# Get current location
LOCATION = str(pathlib.Path(__file__).parent.absolute())
ROOT = rchop(LOCATION, "/core")


# create logger
logger = logging.getLogger('core-library')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class filemanager(object):
    
    def __init__(self):
        with open(ROOT + "/secrets/secrets.json", "r") as fi:
            secrets = json.load(fi)
        
        self.emailAddressFrom = secrets["emailAddressFrom"]
        self.emailAddressTo = secrets["emailAddressTo"]
        self.emailPassword = secrets["emailPassword"]
        self.githubToken = secrets["githubToken"]
        self.stderr_file = ROOT + "/temp/stderr.txt"
        self.stdout_file = ROOT + "/temp/stdout.txt"
        self.hdd1_path = "/media/hdd/"
        self.hdd2_path = "/media/hdd2/"
        
    def is_hdd_safe(self):
        """
        Check to make sure static content is as expected to prevent accidental deletion.
        Guards against issues like the drive being disconnected or randomware having encrypted it
        """
        return self.check_hdd(self.hdd1_path) and self.check_hdd(self.hdd2_path)
    
    def check_hdd(self, path):
        with open(path + "content/XXX-DO-NOT-DELETE/viruscheck.txt", "r") as fi:
            x1 = fi.read().strip()
        with open(path + "content/XXX-DO-NOT-DELETE/viruscheck.csv", "r") as fi:
            x2 = fi.read().strip()
        safe = (x1 == "TEST" and x2 == "TEST")
        if not safe:
            raise FileNotFoundError("Unable to read either viruscheck.txt or viruscheck.csv")
        return safe
        
    def write_std_file(self, content, std, mode="wb"):
        if std == "out":
            file_path = self.stdout_file
        elif std == "err":
            file_path = self.stderr_file
        with open(file_path, mode) as fi:
            fi.write(content)


def run_and_report(cmds, subject, fm, report_sucess=True):
    
    logger.info("Starting run_and_report")
    logger.debug("Commands are:")
    logger.debug(cmds)
    
    # Abort if unsafe
    if not fm.is_hdd_safe():
        sys.exit(1)
    
    logger.info("Starting Proc")
    proc = subprocess.run(cmds, check=False, capture_output=True)
    
    logger.debug("Proc results")
    logger.debug(proc)
    
    fm.write_std_file(proc.stderr, "err")
    fm.write_std_file(proc.stdout, "out")
    
    if proc.returncode != 0 or report_sucess:
        
        result = "SUCCSESS !!" if proc.returncode == 0 else "FAILED !!"
        logger.info("Sending Mail Result = " + result)
            
        send_mail(
            send_to=[fm.emailAddressTo],
            send_from=fm.emailAddressFrom,
            pwd=fm.emailPassword,
            subject=subject + " - " + result,
            text="Return code = {}\nPlease see attachements for details".format(proc.returncode),
            files=[fm.stderr_file, fm.stdout_file]
        )


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


def sync_github(fm):
    
    logger.info("Starting sync_github")
    
    subject = "GitHub Sync"
    REPO_REMOTE = "git@github.com:gowerc/{repo}.git"
    REPO_DIR = "/media/hdd2/GitHub"
    REPO_EXISTING = os.listdir(REPO_DIR)
    
    headers = {"Authorization": "token {t}".format(t=fm.githubToken)}
    
    resp = requests.get(
        url="https://api.github.com/search/repositories?q=user:gowerc",
        headers=headers
    )
    
    resp.raise_for_status()
    
    repo_obj = resp.json()["items"]
    repos = [i["name"] for i in repo_obj]
    
    logger.info("Found repos " + ",".join(repos))
    
    PROC_CLONE = []
    PROC_PULL = []
    
    for repo in repos:
        repo_remote = REPO_REMOTE.format(repo=repo)
        repo_dir = REPO_DIR + "/" + repo
        
        if repo not in REPO_EXISTING:
            proc = subprocess.run(
                ["git", "clone", repo_remote],
                check=False,
                capture_output=True,
                cwd=REPO_DIR
            )
            
            PROC_CLONE.append({
                "repo": repo,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr
            })
        
        proc = subprocess.run(
            ["git", "pull", "--all"],
            check=False,
            capture_output=True,
            cwd=repo_dir
        )
        
        PROC_PULL.append({
                "repo": repo,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr
        })
    
    PROC_ALL = PROC_CLONE + PROC_PULL
    
    stdout = "\n".join([
        "repopisitory = " +
        i["repo"] +
        "\n" +
        i["stdout"].decode("utf-8") +
        "\n"
        for i in PROC_ALL
    ])
    
    stderr = "\n".join([
        "repopisitory = " +
        i["repo"] +
        "\n" +
        i["stderr"].decode("utf-8") +
        "\n"
        for i in PROC_ALL
    ])
    
    status = all([i["returncode"] == 0 for i in PROC_ALL])
    logger.debug("Status = {}".format(status))
    
    fm.write_std_file(stderr, "err", "w")
    fm.write_std_file(stdout, "out", "w")
    
    result = "SUCCSESS !!" if status else "FAILED !!"
    logger.info("Sending Mail Result = " + result)
        
    send_mail(
        send_to=[fm.emailAddressTo],
        send_from=fm.emailAddressFrom,
        pwd=fm.emailPassword,
        subject=subject + " - " + result,
        text="Please see attachements for details",
        files=[fm.stderr_file, fm.stdout_file]
    )
