import os
import subprocess
import sys
import shutil

# ========== CONFIGURATION ==========
SOURCE_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/collateral-tcoe-qa-automation.git"
BRANCH_NAME = "feature/collateral-automation"
NEW_REPO_URL = "ssh://git@bitbucket.cib.echonet:7999/collateralcib/selenium-automation.git"
TEMP_DIR = "jira-rewrite-tmp"
CALLBACK_FILE = "callback.py"
PYTHON_VERSION = "311"  # Adjust if you're using Python 3.10, 3.12, etc
# ===================================

def run(cmd, cwd=None):
    """Run a shell command and exit if it fails."""
    print(f"\n▶ Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print("❌ Command failed:", cmd)
        sys.exit(1)

def find_git_filter_repo():
    """Find git-filter-repo path even if it's not in PATH."""
    user_scripts_dir = os.path.expanduser(f"~\\AppData\\Roaming\\Python\\Python{PYTHON_VERSION}\\Scripts")
    exe_path = os.path.join(user_scripts_dir, "git-filter-repo.exe")
    if os.path.exists(exe_path):
        print(f"✅ Found git-filter-repo at: {exe_path}")
        return f'"{exe_path}"'
    else:
        print("❌ git-filter-repo not found. Please install it with:")
        print("    pip install --user git-filter-repo")
        sys.exit(1)

def clone_branch():
    """Clone only the required branch."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    run(f"git clone --branch {BRANCH_NAME} --single-branch {SOURCE_REPO_URL} {TEMP_DIR}")

def rewrite_commits(git_filter_repo_path):
    """Run git-filter-repo using the callback file."""
    callback_path = os.path.abspath(CALLBACK_FILE)
    run(f"{git_filter_repo_path} --force --message-callback \"{callback_path}\"", cwd=TEMP_DIR)

def push_to_new_repo():
    """Push the rewritten branch to a new remote."""
    run("git remote remove origin", cwd=TEMP_DIR)
    run(f"git remote add origin {NEW_REPO_URL}", cwd=TEMP_DIR)
    run(f"git push --force origin {BRANCH_NAME}", cwd=TEMP_DIR)

def main():
    git_filter_repo_path = find_git_filter_repo()
    clone_branch()
    rewrite_commits(git_filter_repo_path)
    push_to_new_repo()
    print("\n✅ Done! Commits rewritten and pushed with Jira key where needed.")

if __name__ == "__main__":
    main()
