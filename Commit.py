import os
import subprocess
import sys
import shutil

# ===== CONFIGURATION =====
SOURCE_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
TEMP_DIR = "jira-rewrite-tmp"
CALLBACK_FILE = "callback.py"
# =========================

def run(cmd, cwd=None):
    print(f"\nRunning: {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print("❌ Command failed:", cmd)
        sys.exit(1)

def check_git_filter_repo():
    print("✅ Checking if git-filter-repo is installed...")
    result = subprocess.run(["git", "filter-repo", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        print("❌ 'git-filter-repo' is not installed. Install with: pip install git-filter-repo")
        sys.exit(1)

def clone_branch():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO_URL} {TEMP_DIR}")

def rewrite_commits():
    callback_path = os.path.abspath(CALLBACK_FILE)
    run(f"git filter-repo --force --message-callback {callback_path}", cwd=TEMP_DIR)

def push_to_new_repo():
    run("git remote remove origin", cwd=TEMP_DIR)
    run(f"git remote add origin {NEW_REPO_URL}", cwd=TEMP_DIR)
    run(f"git push --force origin {BRANCH_NAME}", cwd=TEMP_DIR)

def main():
    check_git_filter_repo()
    clone_branch()
    rewrite_commits()
    push_to_new_repo()
    print("\n✅ DONE — Jira key added to commit messages missing 'CMIT' or 'QA' and pushed to new repo.")

if __name__ == "__main__":
    main()
