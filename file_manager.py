import os
import yaml

def get_all_relevant_files(folder_path='saved_papers/') -> list:
    files = []
    with os.scandir(folder_path) as entries:
        for entry in entries:
            file_path = folder_path + entry.name
            with open(file_path, 'r') as f:
                load_file = yaml.safe_load(f)
                if load_file['Has Strategy'] == False:
                    continue
                files.append(entry.name)
    return files

