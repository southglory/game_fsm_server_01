# collect_tree.py

import os
import argparse


def write_py_file_tree_with_top_folder(root_folder, output_file, types=["py"], no_ext_files=["Dockerfile", "requirements"], exclude_folders=[], exclude_files=[]):
    root_folder_name = os.path.basename(os.path.normpath(root_folder))  # 최상위 폴더명 가져오기
    with open(output_file, "w") as file:
        for dirpath, _, filenames in os.walk(root_folder):
            # 제외할 폴더명
            if any(folder in dirpath for folder in exclude_folders):
                continue

            # 파일 필터링
            filtered_files = []
            for f in filenames:
                # 제외할 파일 체크
                if any(f.endswith(exclude) for exclude in exclude_files):
                    continue
                # 확장자가 있는 파일 체크
                if any(f.endswith(f".{type}") for type in types):
                    filtered_files.append(f)
                # 확장자가 없는 파일 체크
                elif any(f == no_ext for no_ext in no_ext_files):
                    filtered_files.append(f)

            if filtered_files:
                for f in sorted(filtered_files):
                    # 경로와 파일명을 원하는 형식으로 작성
                    relative_path = os.path.relpath(dirpath, root_folder)
                    full_path = os.path.join(root_folder_name, relative_path)  # 상위 폴더명 포함 경로
                    file.write(f"{full_path}: {f}\n")
    print(output_file, "파일이 생성되었습니다.")


### 사용 예시: python collect_tree.py -p C:\{프로젝트 경로} -o dart_file_tree.txt -t dart
if __name__ == "__main__":
    defaultPath: str = r"C:\Users\coolb\Documents\GitHub_Linked_Projects\wallet_game\wallet_backend"
    defaultOutput: str = os.path.join(r"C:\Users\coolb\Documents\GitHub_Linked_Projects\wallet_game\wallet_backend", "project_tree.txt")
    defaultTypes: list = ["py", "md", "yml", "txt", "http"]
    defaultNoExtFiles: list = ["Dockerfile", "requirements", "LICENSE", "Makefile", ".env.example"]
    exclude_folders: list = ["node_modules", ".git", "venv", "_dev", "pytest_cache"]
    exclude_files: list = ["project_tree.txt"]

    parser = argparse.ArgumentParser(description="Generate a tree of files with top folder.")
    parser.add_argument("-p", "--path", default=defaultPath, help="The root folder to scan.")
    parser.add_argument("-o", "--output", default=defaultOutput, help="The output file to write the tree.")
    parser.add_argument("-t", "--types", default=defaultTypes, help="The file types to scan.")
    parser.add_argument("-n", "--no-ext", default=defaultNoExtFiles, help="Files without extensions to include.")
    parser.add_argument("-e", "--exclude", default=exclude_folders, help="The folders to exclude.")
    parser.add_argument("-x", "--exclude-files", default=exclude_files, help="The files to exclude.")
    args = parser.parse_args()

    write_py_file_tree_with_top_folder(args.path, args.output, args.types, args.no_ext, args.exclude, args.exclude_files)
