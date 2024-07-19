import json
import os

from service import java_parse_svc
from service.git_svc import GitService

target_release_branch_name = "origin/release/20240722_0545"
git_svc = GitService("E:/tmp/hktv-hybris")


def get_branch_diff():
    release_branchs = [branch for branch in git_svc.get_remote_branchs() if branch.name.startswith('origin/release')]
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
                                "committed_date": commit.committed_date}
            commit_diff_info.update(git_svc.get_commit_diff(commit))
            diff_info.append(commit_diff_info)


def get_revamp_related_info(method):
    revamp_paths = []
    remark = ""
    for ann in method.annotations:
        if "EcomRevampServiceMigration" == ann.name:
            for annotation_var in ann.element:
                if "methodPath" == annotation_var.name:
                    for anno_value_entity in annotation_var.value.values:
                        revamp_paths.append(anno_value_entity.value[1:len(anno_value_entity.value) - 1])
                elif "remark" == annotation_var.name:
                    remark = annotation_var.value.value

    result = {}
    if len(revamp_paths) > 0:
        result["related_method"] = revamp_paths
    if len(remark) > 0:
        result["remark"] = remark
    return result


def get_revamp_related_change_list(commit_diff, repo_dir):
    change_list = []
    for key, value in commit_diff.items():
        if "sha" != key and "parent_sha" != key and key.endswith(".java") and not key.endswith(
                "/ThirdPartyLoginPageController.java"):
            file_path = repo_dir + "/" + key
            # change to parent sha
            git_svc.reset(commit_diff["parent_sha"])
            print(f"start analyze changed file, sha[{commit_diff["parent_sha"]}]file_path[{file_path}]")
            if os.path.exists(file_path):
                java_structure = java_parse_svc.get_java_structure(file_path)
                if java_structure:
                    for line_num in value:
                        # find method info
                        method = java_parse_svc.find_method_by_line_number(java_structure, line_num)
                        if method:
                            revamp_related_info = get_revamp_related_info(method)
                            if len(revamp_related_info) > 0:
                                change_list.append({key + ":" + line_num: revamp_related_info})
                else:
                    change_list.append({key + ":9999": {"remark": "cant analyze", "related_method": ["##"]}})
            else:
                change_list.append(
                    {key + ":000": {"remark": "new file", "related_method": ["new file#new file#new file"]}})
    return change_list


def build_revamp_related_change_summary(branch_diff):
    revamp_related_change_summary = []
    for commit_diff in branch_diff:
        revamp_related_change_list = get_revamp_related_change_list(commit_diff, git_svc.__repo_dir__())
        revamp_related_change_summary.append(
            {"sha": commit_diff["sha"], "committed_date": commit_diff["committed_date"],
             "revamp_related_info_list": revamp_related_change_list})
    return sorted(revamp_related_change_summary,
                  key=lambda x: x["committed_date"], reverse=True)


def build_branch_change_summary(revamp_related_change_summary):
    branch_change_summary = {}
    for revamp_related_change in revamp_related_change_summary:
        sha = revamp_related_change["sha"]
        for changeRow in revamp_related_change["revamp_related_info_list"]:
            file_path = list(changeRow.keys())[0]
            if file_path not in branch_change_summary:
                branch_change_summary[file_path] = {}
                branch_change_summary[file_path]["sha"] = [sha]
                branch_change_summary[file_path]["related_method"] = changeRow[file_path]["related_method"]
            else:
                branch_change_summary[file_path]["sha"].append(sha)
    return branch_change_summary


def build_related_service_set(branch_change_summary):
    related_service_set = {""}
    for file_path in branch_change_summary.keys():
        for related_method in branch_change_summary[file_path]["related_method"]:
            related_service_set.add(related_method.split("#")[0])

    related_service_list = []
    for related_service in related_service_set:
        related_service_list.append(related_service)
    return related_service_list


if __name__ == '__main__':
    # get_java_structure("C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/ThirdPartyLoginPageController.java")
    branch_diff = get_branch_diff()
    print(f"hybris target_release_branch_name[{target_release_branch_name}]commits size[{len(branch_diff)}]diff lines[{str(branch_diff)}]")

    revamp_related_change_summary = build_revamp_related_change_summary(branch_diff)
    branch_change_summary = build_branch_change_summary(revamp_related_change_summary)
    related_service_list = build_related_service_set(branch_change_summary)

    output_json = json.dumps({"branch": target_release_branch_name, "commits_change_summary": revamp_related_change_summary,
                              "branch_change_summary": branch_change_summary, "related_service": related_service_list},
                             ensure_ascii=False, indent=4)
    print(output_json)
