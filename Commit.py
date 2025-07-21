import os
import subprocess
import shutil
import sys
import time

# === CONFIGURATION ===
SOURCE_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
WORK_DIR = "jira-rewrite-final"
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

    # Step 1: Clone repo
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO} {WORK_DIR}")
    os.chdir(WORK_DIR)

    # Step 2: Get first commit message
    first_commit = run("git rev-list --max-parents=0 HEAD", capture_output=True).strip()
    original_msg = run(f"git log -1 --format=%s {first_commit}", capture_output=True).strip()

    if JIRA_KEY in original_msg:
        print("✅ Jira key already present. No changes made.")
        return

    new_msg = f"{JIRA_KEY} {original_msg}"
    print(f"🔁 Rewriting first commit to: {new_msg}")

    # Step 3: Start rebase in paused mode
    run("git rebase -i --root", cwd=WORK_DIR)

    # Step 4: Wait until `.git/rebase-merge/message` is created
    msg_path = os.path.join(".git", "rebase-merge", "message")
    for _ in range(10):
        if os.path.exists(msg_path):
            break
        time.sleep(0.5)

    if not os.path.exists(msg_path):
        print("❌ Failed to detect Git rebase message file.")
        sys.exit(1)

    # Step 5: Overwrite commit message
    with open(msg_path, "w", encoding="utf-8") as f:
        f.write(new_msg + "\n")

    # Step 6: Complete the rebase
    run("git rebase --continue")

    # Step 7: Push to new repo
    run("git remote remove origin")
    run(f"git remote add origin {NEW_REPO}")
    run(f"git push --force origin {BRANCH_NAME}")

    print("\n✅ First commit rewritten and pushed successfully!")

if __name__ == "__main__":
    main()
