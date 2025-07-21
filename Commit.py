import os
import subprocess
import sys
import shutil

# ========== CONFIGURATION ==========
SOURCE_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
TEMP_DIR = "jira-rewrite-tmp"
JIRA_KEY = "[JIRA-123]"  # Change to your real Jira ticket
# ===================================

def run(cmd, cwd=None, check=True):
    """Run a shell command and print it."""
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check, cwd=cwd)

def check_git_filter_repo():
    """Ensure git-filter-repo is available."""
    try:
        subprocess.run(["git", "filter-repo", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("❌ 'git-filter-repo' is not installed.")
        print("➡️ Install with: pip install git-filter-repo")
        sys.exit(1)

def clone_branch():
    """Clone only the target branch."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO_URL} {TEMP_DIR}")

def rewrite_commits():
    """Run git-filter-repo with an inline callback expression."""
    message_callback = f"""
import re
def callback(message):
    m = message.decode('utf-8')
    if not re.search(r'(?i)CMIT|QA', m):
        return ('{JIRA_KEY} ' + m).encode('utf-8')
    return message
"""
    run(f'git filter-repo --force --message-callback "{message_callback.strip()}"', cwd=TEMP_DIR)

def push_to_new_repo():
    """Push rewritten branch to new remote."""
    run("git remote remove origin", cwd=TEMP_DIR)
    run(f"git remote add origin {NEW_REPO_URL}", cwd=TEMP_DIR)
    run(f"git push --force origin {BRANCH_NAME}", cwd=TEMP_DIR)

def main():
    check_git_filter_repo()
    clone_branch()
    rewrite_commits()
    push_to_new_repo()
    print("✅ Done. All commits scanned, Jira key added where needed.")

if __name__ == "__main__":
    main()
