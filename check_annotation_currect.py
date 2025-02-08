import os
import re
import shutil
import time
from service import java_parse_svc
from service.git_svc import GitService
from util import cmd_util

revamp_business_master_repo_dir = "E:/Code/shoalter-ecommerce-business"
hybris_dir = 'E:/tmp/hktv-hybris/'
hyris_anno_repo_dir = 'C:/work/hybris_src_code_migration_annotation/'
revamp_infra_master_repo_dir = "E:/Code/shoalter-ecommerce-infra-master-repo/"

def get_has_ann_file():
    # Pattern to search for
    pattern = re.compile(r'@EcomRevamp')

    # List to store the files that contain the pattern
    matching_files = []

    GitService(hybris_dir).checkout("main")
    GitService(hyris_anno_repo_dir).checkout("dev")

    # Walk through the directory
    for subdir, _, files in os.walk(hybris_dir):
        # skip committable dir
        # if subdir.startswith("C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv-dob") or subdir.startswith(
        #         "C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv-oms") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/resources") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/cis") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv") or subdir.startswith(
        #     "C:/work/hybris_docker/hybris_docker_hktvmall/bin/tools"):
        #     continue

        for source_file in files:
            # Check if the file is a .java file
            if source_file.endswith('.java'):
                file_path = os.path.join(subdir, source_file)
                # Open and read the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents = f.read()
                        # Search for the pattern
                        if pattern.search(contents):
                            matching_files.append(file_path)
                except FileNotFoundError:
                    print(f"{file_path} can't be read")

    for subdir, _, files in os.walk(hyris_anno_repo_dir):
        for source_file in files:
            # Check if the file is a .java file
            if source_file.endswith('.java'):
                file_path = os.path.join(subdir, source_file)
                # Open and read the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents = f.read()
                        # Search for the pattern
                        if pattern.search(contents):
                            matching_files.append(file_path)
                except FileNotFoundError:
                    print(f"{file_path} can't be read")
    return matching_files


def get_method_paths(matching_files):
    anno_infos = java_parse_svc.get_revamp_file_anno_info(matching_files)
    method_path_list = []
    for anno_info in anno_infos:
        if "methodPath" in anno_info:
            method_path_list.extend(anno_info["methodPath"])
    fixed_method_path_list = []
    for method_path in method_path_list:
        if "\" + \"" in method_path:
            method_path = method_path.replace("\" + \"", "")
        fixed_method_path_list.append(method_path)
    return fixed_method_path_list


def check_method_exist(method_path):
    methodPathAr = method_path.split("#")
    if len(methodPathAr) < 3:
        return
    anno_service = methodPathAr[0]
    if anno_service == "iims-service":
        anno_service = "hktv-iims"

    anno_clazz_name = methodPathAr[1]
    anno_method_name = methodPathAr[2]
    if "getConsignmentWarehouseAndThirdPartyLogisticsWarehouseOrderEntries" == anno_method_name:
        aa = 1
    methodExist = False
    fileExist = False
    for subdir, _, files in os.walk(revamp_business_master_repo_dir + "/shoalter-ecommerce-business-" + anno_service):
        for file in files:
            if file.endswith(anno_clazz_name + ".java"):
                fileExist = True
                if "getConsignmentWarehouseAndThirdPartyLogisticsWarehouseOrderEntries" == anno_method_name:
                    aa = 1
                file_path = os.path.join(subdir, file)
                java_structure = java_parse_svc.get_java_file_info(file_path)
                if java_structure:
                    revamp_file_method_list = java_structure["methodList"]
                    for revamp_file_method in revamp_file_method_list:
                        if revamp_file_method["name"] == anno_method_name:
                            methodExist = True

    for subdir, _, files in os.walk(revamp_infra_master_repo_dir + "/shoalter-" + anno_service):
        for file in files:
            if file.endswith(anno_clazz_name + ".java"):
                fileExist = True
                if "getConsignmentWarehouseAndThirdPartyLogisticsWarehouseOrderEntries" == anno_method_name:
                    aa = 1
                file_path = os.path.join(subdir, file)
                java_structure = java_parse_svc.get_java_file_info(file_path)
                if java_structure:
                    revamp_file_method_list = java_structure["methodList"]
                    for revamp_file_method in revamp_file_method_list:
                        if revamp_file_method["name"] == anno_method_name:
                            methodExist = True

    if not fileExist:
        print(f"file not exist, anno_clazz_name[{anno_clazz_name}]method_path[{method_path}]")
    elif not methodExist:
        print(
            f"method not exist, anno_clazz_name[{anno_clazz_name}]anno_method_name[{anno_method_name}]method_path[{method_path}]")


def switch_revamp_to_branch(branch):
    return cmd_util.exec(["pullSubmodule.bat", branch], revamp_business_master_repo_dir)


if __name__ == '__main__':
    revamp_target_branch = "dev"

    matching_files = get_has_ann_file()
    print(f"switch revamp master repo project to {revamp_target_branch}")
    switch_revamp_to_branch(revamp_target_branch)
    print("anaylyze hybris file and retrieve method paths")
    methodPaths = get_method_paths(matching_files)
    for methodPath in methodPaths:
        check_method_exist(methodPath)
