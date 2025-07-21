import os
import subprocess
import sys
import shutil

# ========== CONFIGURATION ==========
SOURCE_REPO_URL = "git@yourdomain.com:your/source-repo.git"
BRANCH_NAME = "feature/your-branch-name"
NEW_REPO_URL = "git@yourdomain.com:your/new-repo.git"
TEMP_DIR = "jira-rewrite-tmp"
JIRA_KEY = "[JIRA-123]"
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
    """Clone only a specific branch."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO_URL} {TEMP_DIR}")

def create_rewrite_script():
    """Create a temporary Python script for message rewriting."""
    script = f"""
import re
def callback(message):
    m = message.decode('utf-8')
    if not re.search(r'(?i)CMIT|QA', m):
        return ('{JIRA_KEY} ' + m).encode('utf-8')
    return message
"""
    script_path = os.path.join(TEMP_DIR, "rewrite_commits.py")
    with open(script_path, "w") as f:
        f.write(script.strip())
    return script_path

def rewrite_commits(rewrite_script_path):
    """Run git-filter-repo with the message callback script."""
    run(f"git filter-repo --force --message-callback '{rewrite_script_path}'", cwd=TEMP_DIR)

def push_to_new_repo():
    """Push the rewritten branch to a new remote repo."""
    run("git remote remove origin", cwd=TEMP_DIR)
    run(f"git remote add origin {NEW_REPO_URL}", cwd=TEMP_DIR)
    run(f"git push --force origin {BRANCH_NAME}", cwd=TEMP_DIR)

def main():
    check_git_filter_repo()
    clone_branch()
    script_path = create_rewrite_script()
    rewrite_commits(script_path)
    push_to_new_repo()
    print("✅ Done. Commits updated and pushed with Jira key where needed.")

if __name__ == "__main__":
    main()
