import os
import subprocess
import shutil
import sys

# === CONFIGURATION ===
SOURCE_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
WORK_DIR = "safe-jira-rewrite"
JIRA_KEY = "[JIRA-123]"
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

    # Step 1: Clone specific branch
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO} {WORK_DIR}")

    os.chdir(WORK_DIR)

    # Step 2: Find first commit
    first_commit = run("git rev-list --max-parents=0 HEAD", capture_output=True).strip()
    print(f"🟢 First commit hash: {first_commit}")

    # Step 3: Get commit message
    original_message = run(f"git log -1 --format=%s {first_commit}", capture_output=True).strip()
    print(f"🟢 Original commit message: {original_message}")

    if JIRA_KEY in original_message:
        print("✅ Jira key already present. No change needed.")
        return

    new_message = f"{JIRA_KEY} {original_message}"
    print(f"📝 New message: {new_message}")

    # Step 4: Create new commit object with modified message
    run(f"git cat-file commit {first_commit} > commit.txt")
    with open("commit.txt", "r") as f:
        lines = f.readlines()

    # Replace commit message
    idx = lines.index('\n')
    lines = lines[:idx+1] + [new_message + '\n']

    with open("new_commit.txt", "w") as f:
        f.writelines(lines)

    # Create new commit object
    new_commit = run("git hash-object -t commit -w new_commit.txt", capture_output=True).strip()
    print(f"🆕 New commit hash: {new_commit}")

    # Step 5: Replace first commit with new one
    run(f"git replace {first_commit} {new_commit}")

    # Step 6: Export and re-import repo (to bake in the change)
    run("git fast-export --all > repo.export")
    os.chdir("..")
    shutil.rmtree("final-push", ignore_errors=True)
    run("git init final-push")
    os.chdir("final-push")
    run("git fast-import < ../safe-jira-rewrite/repo.export")

    # Step 7: Push to new repo
    run(f"git remote add origin {NEW_REPO}")
    run(f"git push --force origin {BRANCH_NAME}")

    print("\n✅ Done! First commit updated and pushed without conflict.")

if __name__ == "__main__":
    main()
