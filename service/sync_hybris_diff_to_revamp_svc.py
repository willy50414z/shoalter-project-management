import json
import os
import re
from datetime import datetime

from service import java_parse_svc
from service.git_svc import GitService


class SyncHybrisDiffToRevampService():
    def __init__(self, project_root_dir):
        self.git_svc = GitService(project_root_dir)

    def get_branch_shas(self, end_commit_sha):
        head_sha = self.git_svc.get_head_sha()
        rev = self.git_svc.get_first_rev(head_sha)
        branch_shas = []
        while True:
            branch_shas.append(rev[0])
            if len(branch_shas) > 500:
                raise ValueError("commits size is more than 500, please check end_commit_sha in this branch")
            if rev[0] == end_commit_sha:
                return branch_shas
            rev = self.git_svc.get_first_rev(rev[1])

    def get_branch_diff(self, branch_name, end_commit_sha):
        diff_info = []
        branch_commit_shas = self.get_branch_shas(end_commit_sha)

        commits = self.git_svc.get_branch_commits(branch_name)
        for commit in commits:
            if end_commit_sha == commit.hexsha:
                return diff_info
            elif commit.hexsha in branch_commit_shas:
                commit_diff_info = {"sha": commit.hexsha, "parent_sha": commit.parents[0].hexsha,
                                    "committed_date": commit.committed_date, "commit_msg": commit.message}
                commit_diff_info.update(self.git_svc.get_commit_diff(commit))
                diff_info.append(commit_diff_info)

    def get_release_branch_diff(self, target_release_branch_name):
        release_branchs = [branch for branch in self.git_svc.get_remote_branchs() if
                           branch.name.startswith('origin/release')]
        release_branchs = sorted(release_branchs, key=lambda x: x.name, reverse=True)

        target_release_branch = None
        last_release_sha = None
        for branch in release_branchs:
            if target_release_branch:
                last_release_sha = branch.commit.hexsha
                print(f"analyze diff from {branch.name} to {target_release_branch.name}")
                break
            if target_release_branch_name == branch.name:
                target_release_branch = branch

        commits = list(target_release_branch.commit.iter_parents())
        commits.insert(0, target_release_branch.commit)

        diff_info = []
        for commit in commits:
            if commit.hexsha == last_release_sha:
                return diff_info
            if not commit.message.startswith("Merge remote-tracking branch"):
                commit_diff_info = {"sha": commit.hexsha, "parent_sha": commit.parents[0].hexsha,
                                    "committed_date": commit.committed_date, "commit_msg": commit.message}
                commit_diff_info.update(self.git_svc.get_commit_diff(commit))
                diff_info.append(commit_diff_info)

    def get_revamp_related_info(self, method):
        revamp_method_anno_info = java_parse_svc.get_revamp_method_anno_info(method)
        result = {}
        if java_parse_svc.ANNOTATION_KEY_METHOD_PATH in revamp_method_anno_info:
            result["related_method"] = revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_METHOD_PATH]
        if java_parse_svc.ANNOTATION_KEY_REMARK in revamp_method_anno_info:
            result["remark"] = revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_REMARK]
        return result

    def is_file_contains_annotation(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            contents = f.read()
            pattern = re.compile(r'@EcomRevamp')
            return pattern.search(contents)

    def get_revamp_related_change_list(self, commit_diff, repo_dir):
        change_list = []
        for key, value in commit_diff.items():
            if "sha" != key and "parent_sha" != key and key.endswith(".java") and not key.endswith(
                    "/EcomRevampServiceMigration.java"):
                file_path = repo_dir + "/" + key
                # change to parent sha
                self.git_svc.reset(commit_diff["parent_sha"])
                print(f"start analyze changed file, sha[{commit_diff["parent_sha"]}]file_path[{file_path}]")
                if os.path.exists(file_path) and self.is_file_contains_annotation(file_path):
                    java_file_info = java_parse_svc.get_java_file_info(file_path)
                    if java_file_info:
                        for line_num in value:
                            # find method info
                            method = java_parse_svc.find_method_by_line_number(java_file_info, line_num)
                            if method:
                                revamp_related_info = self.get_revamp_related_info(method)
                                if len(revamp_related_info) > 0:
                                    change_list.append({key + ":" + line_num: revamp_related_info})
                    else:
                        # change_list.append({key + ":9999": {"remark": "cant analyze", "related_method": ["##"]}})
                        raise ValueError(f"can't analyze file[{file_path}]")
                else:
                    change_list.append(
                        {key + ":000": {"remark": "new file", "related_method": ["new file#new file#new file"]}})
        return change_list

    def build_revamp_related_change_summary(self, branch_diff):
        revamp_related_change_summary = []
        for commit_diff in branch_diff:
            revamp_related_change_list = self.get_revamp_related_change_list(commit_diff, self.git_svc.__repo_dir__())
            revamp_related_change_summary.append(
                {"sha": commit_diff["sha"], "commit_msg": commit_diff["commit_msg"],
                 "committed_date": datetime.fromtimestamp(commit_diff["committed_date"]).strftime('%Y-%m-%d %H:%M'),
                 "revamp_related_info_list": revamp_related_change_list})
        return sorted(revamp_related_change_summary,
                      key=lambda x: x["committed_date"], reverse=True)

    def build_branch_change_summary(self, revamp_related_change_summary):
        branch_change_summary = {}
        for revamp_related_change in revamp_related_change_summary:
            sha = revamp_related_change["sha"]
            commit_msg = revamp_related_change["commit_msg"]
            for changeRow in revamp_related_change["revamp_related_info_list"]:
                file_path = list(changeRow.keys())[0]
                if file_path not in branch_change_summary:
                    branch_change_summary[file_path] = {}
                    branch_change_summary[file_path]["sha"] = [sha]
                    branch_change_summary[file_path]["commit_msg"] = [commit_msg]
                    if "related_method" in changeRow[file_path]:
                        branch_change_summary[file_path]["related_method"] = changeRow[file_path]["related_method"]
                else:
                    branch_change_summary[file_path]["sha"].append(sha)
                    branch_change_summary[file_path]["commit_msg"].append(commit_msg)
        return branch_change_summary

    def build_related_service_set(self, branch_change_summary):
        related_service_set = {""}
        for file_path in branch_change_summary.keys():
            for related_method in branch_change_summary[file_path]["related_method"]:
                related_service_set.add(related_method.split("#")[0])

        related_service_list = []
        for related_service in related_service_set:
            related_service_list.append(related_service)
        return related_service_list

    def build_related_commit_list(self, branch_change_summary):
        related_service_set = {""}
        for file_path in branch_change_summary.keys():
            for related_method in branch_change_summary[file_path]["commit_msg"]:
                related_service_set.add(related_method.split("#")[0])

        related_service_list = []
        for related_service in related_service_set:
            related_service_list.append(related_service)
        return related_service_list

    def build_related_file_list(self, branch_change_summary):
        related_service_set = {""}
        for file_path in branch_change_summary.keys():
            related_service_set.add(file_path[0:file_path.rfind(":")])

        related_service_list = []
        for related_service in related_service_set:
            related_service_list.append(related_service)
        return related_service_list

    def build_change_summary_response(self, branch_name, branch_diffs):
        print(f"hybris branch[{branch_name}]commits size[{len(branch_diffs)}]diff lines[{str(branch_diffs)}]")

        revamp_related_change_summary = self.build_revamp_related_change_summary(branch_diffs)
        branch_change_summary = self.build_branch_change_summary(
            revamp_related_change_summary)
        related_service_list = self.build_related_service_set(branch_change_summary)
        related_commit_list = self.build_related_commit_list(branch_change_summary)
        related_file_list = self.build_related_file_list(branch_change_summary)

        return json.dumps({"branch": branch_name, "commits_change_summary": revamp_related_change_summary,
                           "branch_change_summary": branch_change_summary,
                           "related_service": related_service_list, "related_commit": related_commit_list,
                           "related_file": related_file_list},
                          ensure_ascii=False, indent=4)

    def get_branch_change_summary(self, branch_name, end_commit_sha):
        branch_diff = self.get_branch_diff(branch_name, end_commit_sha)
        return self.build_change_summary_response(branch_name, branch_diff)

    def get_release_change_summary(self, target_release_branch_name):
        branch_diff = self.get_release_branch_diff(target_release_branch_name)
        return self.build_change_summary_response(target_release_branch_name, branch_diff)
