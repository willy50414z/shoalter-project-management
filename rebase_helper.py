import git
import os

# Path to your git repository
# repo_path = 'C:/work/hybris_docker/hybris_docker_hktvmall/bin/'
# repo_path = 'E:/tmp/testgit/'
repo_path = "E:/Code/hktv-hybris"

# conflict_resolve_strategy = '--theirs'
conflict_resolve_strategy = '--ours'

# Initialize the repo
repo = git.Repo(repo_path)


def run_rebase_continue():
    try:
        # Run `git rebase --continue`
        repo.git.rebase('--continue')
    except git.GitCommandError as e:
        print(f"Rebase failed: {e}")


def check_and_resolve_conflicts():
    # Get the list of files with conflicts
    conflicted_files = repo.index.unmerged_blobs()

    conflicts_resolved = True
    manual_file = []
    for file_path in conflicted_files:
        file_name = os.path.basename(file_path)

        isJava = False

        if file_name.endswith(".java"):
            isJava = True
            # Read the content of the conflicted file
            with open(os.path.join(repo_path, file_path), 'r', encoding='utf-8') as file:
                content = file.read()

        # Check if 'EcomRevampServiceMigration' is in the file

        if not isJava or 'EcomRevampServiceMigration' not in content:
            # Accept 'theirs' changes
            # repo.git.checkout('--theirs', file_path)
            repo.git.execute(['git', 'checkout', conflict_resolve_strategy, file_path])
            print(f'resolve {file_path} by ours')
            # repo.index.add([file_path])
        else:
            manual_file.append(file_path)
            conflicts_resolved = False
    for file_path in manual_file:
        print(f"{file_path} need resolve mannual")
    return conflicts_resolved


def get_commit_message():
    commit_message_file_path = os.path.join(repo.git_dir, 'rebase-merge', 'message')
    with open(commit_message_file_path, 'r') as f:
        commit_message = f.read().strip()
    return commit_message


def get_commit_sha():
    commit_sha_file_path = os.path.join(repo.git_dir, 'rebase-merge', 'stopped-sha')
    with open(commit_sha_file_path, 'r') as f:
        commit_sha = f.read().strip()
    return commit_sha


if __name__ == "__main__":
    while True:
        # Run rebase --continue
        print("start rebase --continue")
        run_rebase_continue()

        # Check for conflicts
        if repo.index.unmerged_blobs():
            if check_and_resolve_conflicts():
                # If all conflicts resolved, run rebase --continue again
                repo.git.add(A=True)
                if repo.is_dirty():
                    repo.git.commit('-m', 'Resolved all conflicts and accepted ours changes, '
                                    f'origin commit_sha[{get_commit_sha()}]origin commit_message[{get_commit_message()}]')
                else:
                    print('ready for continue rebase')
            else:
                print("Conflicts not resolved. Please resolve manually.")
                repo.git.add(A=True)
                if repo.is_dirty():
                    repo.git.commit('-m',
                                    f'Resolved all conflicts and accepted ours changes and manual resolve, '
                                    f'origin commit_sha[{get_commit_sha()}]origin commit_message[{get_commit_message()}]')
                else:
                    print('ready for continue rebase')
        else:
            print("no conflict.")
            # repo.git.add(A=True)
            # if repo.is_dirty():
            #     repo.git.commit('-a -m', 'commit without conflict')
            # else:
            #     print('ready for continue rebase')
    # repo.git.execute(['git', 'checkout', '--ours', 'aa.txt'])
    # repo.git.add(A=True)
    # repo.git.commit('-m', 'Resolved all conflicts and accepted ours changes')
