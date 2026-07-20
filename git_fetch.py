from gitingest import ingest_async, ingest
import pickle
import re
import os

DEFAULT_EXCLUDE_PATTERN = ["docs/", ".github"]

def file_chunks(file_str) -> dict:
    files = {}

    chunks = re.split(r"={10,}\nFILE: (.+?)\n={10,}\n", file_str)

    for path, body in zip(chunks[1::2], chunks[2::2]):
        files[path] = body
    return files

def fetch_github_repo(repo_title, exclude_pattern=DEFAULT_EXCLUDE_PATTERN, file_path='github_data.pkl'):
    data = pickle.load(open(file_path, 'rb')) if os.path.exists(file_path) else {}
    if len(data.keys()) == 0 or repo_title not in data.keys():
        summary, tree, content = ingest(
            repo_title,
            exclude_patterns=exclude_pattern,
        )
        files_data = file_chunks(content)
        data[repo_title] = {
                            'ingest': (summary, tree, content),
                            'files_data': files_data}
        pickle.dump(data, open(file_path, 'wb'))
    return data

async def fetch_github_repo_async(repo_title, exclude_pattern=DEFAULT_EXCLUDE_PATTERN, file_path='github_data.pkl'):
    data = pickle.load(open(file_path, 'rb')) if os.path.exists(file_path) else {}
    if len(data.keys()) == 0 or repo_title not in data.keys():
        summary, tree, content = await ingest_async(
            repo_title,
            exclude_patterns=exclude_pattern,
        )
        files_data = file_chunks(content)
        data[repo_title] = {
                            'ingest': (summary, tree, content),
                            'files_data': files_data}
        pickle.dump(data, open(file_path, 'wb'))
    return data