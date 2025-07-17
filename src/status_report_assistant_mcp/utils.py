import os

def get_parent_directory(path: str):
    abs_path = os.path.expanduser(path)
    path_parts = abs_path.split("/")
    path_parts.pop()
    return "/".join(path_parts)
