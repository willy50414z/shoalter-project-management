import os
import re
import shutil
import time

if __name__ == '__main__':
    start_time = time.time()
    root_dir = 'C:\\work\\hybris_docker\\hybris_docker_hktvmall\\bin\\'
    target_root_dir = 'C:\\work\\hybris_src_code_migration_annotation\\bin\\'

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

    # Print the matching files
    for has_anno_file in matching_files:
        source_dir = os.path.dirname(has_anno_file)
        target_dir = source_dir.replace(root_dir, target_root_dir)
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, os.path.basename(has_anno_file))
        shutil.copy(has_anno_file, target_file)
        print(f"copy {has_anno_file} to {target_file}")
    print(f"Method execution time: {time.time() - start_time} seconds")
