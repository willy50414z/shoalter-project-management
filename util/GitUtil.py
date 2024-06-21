import git


def merge_and_push(repo_path, source, target):
    # Open the repository
    repo = git.Repo(repo_path)

    # Fetch latest changes from remote
    repo.remotes.origin.fetch()

    repo.git.checkout(source)

    # Checkout the target branch
    repo.git.checkout(target)

    # Merge the source branch into the target branch
    repo.git.merge(source)

    return repo.remotes.origin.push()


def get_branch_commits(repo_path, branch_name):
    repo = git.Repo(repo_path)
    checkout(repo_path, "dev")
    if branch_name in repo.branches:
        repo.delete_head(branch_name, force=True)
    checkout(repo_path, branch_name)

    branch = repo.branches[branch_name]
    commits = list(branch.commit.iter_parents())
    commits.insert(0, branch.commit)
    return commits

def checkout(repo_path, branch_name):
    repo = git.Repo(repo_path)
    if branch_name not in repo.branches:
        repo.remotes.origin.fetch()
    repo.git.checkout(branch_name)


def get_commit_diff(repo_path, commit):
    repo = git.Repo(repo_path)
    diff = repo.git.diff(commit.parents[0].hexsha, commit.hexsha, '--unified=0')

    file_path = ""
    commit_diff = {}
    line_num = ""
    for line in diff.split("\n"):
        if line.startswith("--- a/"):
            file_path = line[6:]
            if file_path not in commit_diff:
                commit_diff[file_path] = []
        elif line.startswith("@@"):
            #add new file no need to check
            if "" == file_path:
                continue
            line_num = line[4:]
            line_num = line_num[:min(line_num.find(" "), line_num.find(",")) if "," in line_num else line_num.find(" ")]
            commit_diff[file_path].append(line_num)
        # elif line.startswith("-\t@") or line.startswith("+\t@") and line_num in commit_diff[file_path]:
        #     # 排除只有annotation的change
        #     commit_diff[file_path].remove(line_num)

    return commit_diff


def reset(repo_path, sha):
    repo = git.Repo(repo_path)
    repo.git.reset(sha, hard=True)

def clone(repo_url, clone_dir):
    return git.Repo.clone_from(repo_url, clone_dir)
