import os
import subprocess
import shutil
import sys

# === CONFIGURATION ===
SOURCE_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
WORK_DIR = "jira-rewrite-safe"
JIRA_KEY = "[CMIT-9999]"
# =====================

def run(cmd, cwd=None, capture_output=False):
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture_output, text=True)
    if result.returncode != 0:
        print("❌ Command failed")
        print(result.stderr)
        sys.exit(1)
    return result.stdout if capture_output else None

def main():
    if os.path.exists(WORK_DIR):
        shutil.rmtree(WORK_DIR)

    # Step 1: Clone the repo
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO} {WORK_DIR}")
    os.chdir(WORK_DIR)

    # Step 2: Get first commit
    first_commit = run("git rev-list --max-parents=0 HEAD", capture_output=True).strip()
    original_message = run(f"git log -1 --format=%s {first_commit}", capture_output=True).strip()
    print(f"🟢 First Commit: {first_commit}")
    print(f"🟢 Message: {original_message}")

    if JIRA_KEY in original_message:
        print("✅ Jira key already exists.")
        return

    new_message = f"{JIRA_KEY} {original_message}"

    # Step 3: Set editor to auto-rewrite message
    os.environ["GIT_EDITOR"] = f"sed -i '1s/.*/{new_message}/'"
    run("git rebase -i --root --autosquash")

    # Step 4: Push to new repo
    run("git remote remove origin")
    run(f"git remote add origin {NEW_REPO}")
    run(f"git push --force origin {BRANCH_NAME}")

    print("\n✅ First commit rewritten with Jira key and pushed successfully!")

if __name__ == "__main__":
    main()
