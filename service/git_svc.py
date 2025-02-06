import subprocess

import git


class GitService:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.repo = git.Repo(repo_dir)

    def __repo_dir__(self):
        return self.repo_dir

    def pull(self):
        self.repo.remotes.origin.pull()

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

    def get_head_sha(self):
        return self.repo.head.commit.hexsha

    def get_branch_commits(self, branch_name):
        self.delete_and_checkout(branch_name)

        branch = self.repo.branches[branch_name]
        commits = list(branch.commit.iter_parents())
        commits.insert(0, branch.commit)
        return commits

    def checkout(self, branch_name):
        if branch_name not in self.repo.branches:
            self.repo.remotes.origin.fetch()
        self.repo.git.checkout(branch_name)
        self.repo.remotes.origin.pull()

    def delete_and_checkout(self, branch_name):
        self.checkout("dev")
        if branch_name in self.repo.branches:
            self.repo.delete_head(branch_name, force=True)
        self.checkout(branch_name)

    def create_branch(self, base_branch, new_branch_name):
        if base_branch in self.repo.heads:
            self.delete_and_checkout(base_branch)
        else:
            origin = self.repo.remotes.origin
            origin.fetch()
            self.repo.create_head(base_branch, origin.refs.staging).set_tracking_branch(origin.refs.staging)
            self.repo.git.checkout(base_branch)

        if new_branch_name in self.repo.heads:
            self.repo.delete_head(new_branch_name, force=True)

        new_branch = self.repo.create_head(new_branch_name)
        new_branch.checkout()
        print(f"Branch '{new_branch_name}' created and checked out.")

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

    def commit_and_push(self, commit_message, branch_name):
        """
        Commit local changes and push to a remote Git repository.

        :param repo_path: Path to the local Git repository.
        :param commit_message: Commit message for the changes.
        :param branch_name: The branch to push changes to.
        :param remote_name: The name of the remote repository (default: 'origin').
        """
        try:
            remote_name = 'origin'
            # Check for untracked files and stage them
            self.repo.git.add(A=True)  # Adds all changes (staged and unstaged)

            # Check if there are changes to commit
            if self.repo.is_dirty(untracked_files=True):
                # Commit the changes
                self.repo.index.commit(commit_message)
                print(f"Committed changes with message: '{commit_message}'")
            else:
                print("No changes to commit.")
                return

            # Push to the remote repository
            # origin = self.repo.remote(name=remote_name)
            # origin.push(refspec=f"{branch_name}:{branch_name}")
            self.repo.git.push("--set-upstream", "origin", branch_name)
            print(f"Pushed changes to {remote_name}/{branch_name}")
        except git.exc.GitCommandError as e:
            print(f"Git command error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get_first_rev(self, sha):
        try:
            cmd = [
                "git", f"rev-list", "--parents", "-n", "1", sha
            ]
            output = subprocess.run(cmd, check=True,  # Raises an exception if the command fails
                                    stdout=subprocess.PIPE,  # Captures the standard output
                                    stderr=subprocess.PIPE,  # Captures the standard error
                                    cwd=self.repo_dir
                                    )
            raw_rev = output.stdout.__str__()
            rev = raw_rev[2:len(raw_rev) - 3]
            return rev.split(" ")
        except subprocess.CalledProcessError as e:
            print(f"Error updating property: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")