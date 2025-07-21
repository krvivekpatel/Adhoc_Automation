import os
import subprocess
import shutil
import sys

# === CONFIGURATION ===
SOURCE_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
WORK_DIR = "safe-jira-rewrite"
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

    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO} {WORK_DIR}")
    os.chdir(WORK_DIR)

    # Get first commit
    first_commit = run("git rev-list --max-parents=0 HEAD", capture_output=True).strip()
    print(f"🟢 First commit hash: {first_commit}")

    # Dump full commit content
    full_commit = run(f"git cat-file -p {first_commit}", capture_output=True)
    lines = full_commit.splitlines()

    # Separate header and message
    header_lines = []
    message_lines = []
    blank_found = False

    for line in lines:
        if not blank_found:
            if line.strip() == "":
                blank_found = True
            header_lines.append(line)
        else:
            message_lines.append(line)

    original_message = "\n".join(message_lines).strip()
    print(f"🟢 Original message: {original_message}")

    if JIRA_KEY in original_message:
        print("✅ Jira key already present. No need to modify.")
        return

    new_message = f"{JIRA_KEY} {original_message}"

    # Write new commit file
    with open("new_commit.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(header_lines) + "\n\n" + new_message + "\n")

    new_commit_sha = run("git hash-object -t commit -w new_commit.txt", capture_output=True).strip()
    print(f"🆕 New commit created: {new_commit_sha}")

    # Replace first commit
    run(f"git replace {first_commit} {new_commit_sha}")

    # Export & re-import full history with updated commit
    run("git fast-export --all > ../repo.export")
    os.chdir("..")
    shutil.rmtree("final-push", ignore_errors=True)
    run("git init final-push")
    os.chdir("final-push")
    run("git fast-import < ../repo.export")

    # Push to new repo
    run(f"git remote add origin {NEW_REPO}")
    run(f"git push --force origin {BRANCH_NAME}")

    print("\n✅ First commit updated and pushed successfully!")

if __name__ == "__main__":
    main()
