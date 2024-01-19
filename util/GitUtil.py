import subprocess
from git import Repo

repo_path = "C:/work/shoalter-ecommerce-business-address-service/"
repo = Repo(repo_path)

def get_last_change_date(branch_name):
    try:
        branch = repo.branches[branch_name]
        last_commit = branch.commit
        last_change_date = last_commit.committed_datetime
        return last_change_date
    except Exception as e:
        print("An error occurred:", e)
        return None

def get_remote_branchs_name():
    remote_branches = [ref.name for ref in repo.remotes.origin.refs]
    return remote_branches

def get_last_change_date1(branch_name):
    remote_branches = repo.remotes.origin.refs
    print("Last push dates for remote branches:")
    for branch in remote_branches:
        if branch.remote_head == "HEAD":
            # Skip the HEAD reference
            continue
        # Get the last commit hash for the branch
        commit_hash = repo.rev_parse(branch.remote_head)

        # Use git log command to get the last commit date
        command = ["git", "log", "-n", "1", "--format=%ci", commit_hash]
        last_commit_date = subprocess.check_output(command, cwd=repo_path, text=True).strip()

# remote_branches = get_remote_branchs_name()
# remote_branches = ["dev"]
# for branch in remote_branches:
    # print(branch + ' - ' + str(get_last_change_date(branch)) + ' - ' + get_last_change_date1(branch))

# Replace with the URL of your remote Git repository
remote_repo_url = 'https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/business_module/shoalter-ecommerce-business-address-service.git'

# Replace with the name of the remote branch you want to query
remote_branch_name = 'dev'

# Fetch the latest changes from the remote repository
git_fetch_cmd = ['git', 'fetch', '--all']
subprocess.run(git_fetch_cmd, check=True)

# Execute 'git log -1 --format=%ci origin/<branch_name>' command to get last push date
git_cmd = ['git', 'log', '-1', '--format=%ci', f'origin/{remote_branch_name}']
try:
    last_push_date = subprocess.check_output(git_cmd, cwd=repo_path, text=True).strip()
    print(f"Last push date of '{remote_branch_name}': {last_push_date}")
except subprocess.CalledProcessError as e:
    print(f"Error retrieving push date for branch '{remote_branch_name}': {e}")