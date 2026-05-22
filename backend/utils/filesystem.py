import os


def get_files(folder, tracked_files):
    result = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder)
            relative_path = relative_path.replace('\\', '/')
            if relative_path not in tracked_files:
                result.append(relative_path)
    return result


def cleanup_empty_dirs(folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
