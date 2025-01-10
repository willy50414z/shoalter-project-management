import os
import re
import shutil
import time

from service import java_parse_svc

root_dir = 'C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\'


def search_file_with_engine_anno():
    # Pattern to search for
    pattern = re.compile(r'@EcomRevamp')

    # List to store the files that contain the pattern
    matching_files = []

    # Walk through the directory
    for subdir, _, files in os.walk(root_dir):
        # skip committable dir
        if subdir.startswith("C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\ext-hktv-dob") or subdir.startswith(
                "C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\ext-hktv-oms") or subdir.startswith(
            "C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\resources") or subdir.startswith(
            "C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\cis") or subdir.startswith(
            "C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\ext-hktv") or subdir.startswith(
            "C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\tools"):
            continue

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


def get_revamp_related_info(method):
    revamp_method_anno_info = java_parse_svc.get_revamp_method_anno_info(method)
    result = {}
    if len(revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_METHOD_PATH]) > 0:
        result["related_method"] = revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_METHOD_PATH]
    if len(revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_REMARK]) > 0:
        result["remark"] = revamp_method_anno_info[java_parse_svc.ANNOTATION_KEY_REMARK]
    return result


if __name__ == '__main__':
    matching_files = search_file_with_engine_anno()
    for file in matching_files:
        java_structure = java_parse_svc.get_java_structure(file)
        if java_structure:
            for line_num in value:
                # find method info
                method = java_parse_svc.find_method_by_line_number(java_structure, line_num)
                if method:
                    revamp_related_info = get_revamp_related_info(method)
