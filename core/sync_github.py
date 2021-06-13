import subprocess
import logging
import requests
import os
import core
logger = logging.getLogger(__name__)


def main(secrets):
    logger.info("Starting sync_github")

    REPO_REMOTE = "git@github.com:gowerc/{repo}.git"
    REPO_DIR = "/media/hdd2/GitHub"
    REPO_EXISTING = os.listdir(REPO_DIR)

    headers = {"Authorization": "token {t}".format(t=secrets["githubToken"])}

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

        logger.info("Dealing with " + repo)

        if repo not in REPO_EXISTING:
            proc = subprocess.run(
                ["git", "clone", repo_remote],
                check=False,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                cwd=REPO_DIR
            )

            PROC_CLONE.append({
                "repo": repo,
                "returncode": proc.returncode,
                "stdout": proc.stdout
            })

        proc = subprocess.run(
            ["git", "pull", "--all"],
            check=False,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            cwd=repo_dir
        )

        PROC_PULL.append({
            "repo": repo,
            "returncode": proc.returncode,
            "stdout": proc.stdout
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

    status = all([i["returncode"] == 0 for i in PROC_ALL])

    return core.result(
        log=stdout,
        success=status,
        subject="GitHub Sync"
    )
