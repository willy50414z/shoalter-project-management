import git


class GitService:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.repo = git.Repo(repo_dir)

    def __repo_dir__(self):
        return self.repo_dir

    def merge_and_push(self, source, target):
        # Fetch latest changes from remote
        self.repo.remotes.origin.fetch()

        self.repo.git.checkout(source)

        self.repo.remote().update()

        # Checkout the target branch
        self.repo.git.checkout(target)

        # Merge the source branch into the target branch
        self.repo.git.merge(source)

        return self.repo.remotes.origin.push()

    def get_remote_branchs(self):
        return self.repo.remotes.origin.refs

    def get_branch_commits(self, branch_name):
        self.checkout("dev")
        if branch_name in self.repo.branches:
            self.repo.delete_head(branch_name, force=True)
        self.checkout(branch_name)

        branch = self.repo.branches[branch_name]
        commits = list(branch.commit.iter_parents())
        commits.insert(0, branch.commit)
        return commits

    def checkout(self, branch_name):
        if branch_name not in self.repo.branches:
            self.repo.remotes.origin.fetch()
        self.repo.git.checkout(branch_name)

    def get_commit_diff(self, commit):
        diff = self.repo.git.diff(commit.parents[0].hexsha, commit.hexsha, '--unified=0')

        file_path = ""
        commit_diff = {}
        line_num = ""
        for line in diff.split("\n"):
            if line.startswith("+++ b/"):
                file_path = line[6:]
                if file_path not in commit_diff:
                    commit_diff[file_path] = []
            elif line.startswith("@@"):
                # add new file no need to check
                if "" == file_path:
                    continue
                line_num = line[4:]
                line_num = line_num[
                           :min(line_num.find(" "), line_num.find(",")) if "," in line_num else line_num.find(" ")]
                commit_diff[file_path].append(line_num)
            # elif line.startswith("-\t@") or line.startswith("+\t@") and line_num in commit_diff[file_path]:
            #     # 排除只有annotation的change
            #     commit_diff[file_path].remove(line_num)

        return commit_diff

    def reset(self, sha):
        self.repo.git.reset(sha, hard=True)

    def clone(repo_url, clone_dir):
        return git.Repo.clone_from(repo_url, clone_dir)
