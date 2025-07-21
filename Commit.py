import os
import subprocess
import shutil
import sys

# CONFIG
SOURCE_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
WORK_DIR = "first-commit-fix"
JIRA_KEY = "[JIRA-123]"

def run(cmd, cwd=None):
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print("❌ Command failed")
        sys.exit(1)

def fix_first_commit():
    if os.path.exists(WORK_DIR):
        shutil.rmtree(WORK_DIR)

    # Step 1: Clone the repo
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO} {WORK_DIR}")

    # Step 2: Rebase interactively from root and edit first commit
    git_dir = os.path.abspath(WORK_DIR)
    os.chdir(git_dir)

    # Use environment to reword automatically
    run("git rebase -i --root --autosquash", cwd=git_dir)

    # Step 3: Modify the first commit message
    result = subprocess.run(["git", "log", "--format=%H", "--reverse"], capture_output=True, text=True)
    first_commit_hash = result.stdout.splitlines()[0]

    result = subprocess.run(["git", "log", "-1", "--format=%s", first_commit_hash], capture_output=True, text=True)
    original_message = result.stdout.strip()

    if JIRA_KEY not in original_message:
        new_message = f"{JIRA_KEY} {original_message}"
        run(f'git commit --amend -m "{new_message}" --allow-empty', cwd=git_dir)

    # Step 4: Push to new remote
    run("git remote remove origin", cwd=git_dir)
    run(f"git remote add origin {NEW_REPO}", cwd=git_dir)
    run(f"git push --force origin {BRANCH_NAME}", cwd=git_dir)

    print("\n✅ First commit rewritten with Jira key and pushed!")

if __name__ == "__main__":
    fix_first_commit()
