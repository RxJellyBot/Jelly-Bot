"""Script to run after deployment."""
from datetime import datetime
import subprocess

LOG_PATH = "../logs/Jelly-Bot/Application/deploy.log"


def get_current_commit_hash():
    """Get the current commit hash in short by calling ``git`` command via terminal."""
    cmd = "git rev-parse --verify --short HEAD"

    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]


def get_current_branch_name():
    """Get the current branch name. Only works for Git 2.22+."""
    cmd = "git branch --show-current"

    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")[:-1]


def log_commit(branch_name: str, commit_hash: str, log_path: str = LOG_PATH):
    """Log deployment commit status and the current time in UTC to ``log_path``"""
    message = f"[{datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')} (UTC)] " \
              f"Deployed {branch_name} / {commit_hash}\n"

    with open(log_path, "a+") as f:
        f.write(message)

    print(message)
    print("=== Deployment logged ===")


def main():
    """Main process."""
    branch_name = get_current_branch_name()
    commit_hash = get_current_commit_hash()
    log_commit(branch_name, commit_hash)


if __name__ == '__main__':
    main()
