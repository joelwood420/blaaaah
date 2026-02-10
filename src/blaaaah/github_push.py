from typing import Optional
from .auth import get_saved_token
from github import Github


def push_reflection(repo_full_name: str, path: str, content: str, token: Optional[str] = None) -> bool:
    """Push a file to the given GitHub repository using a saved token.

    repo_full_name should be like 'owner/repo'. Path is the file path in the repo.
    Returns True on success, False otherwise.
    """
    token = token or get_saved_token()
    if not token:
        return False
    try:
        gh = Github(token)
        repo = gh.get_repo(repo_full_name)
    except Exception:
        return False
    try:
        # try to get existing file
        contents = repo.get_contents(path)
        repo.update_file(contents.path, f"Update reflection {path}", content, contents.sha)
    except Exception:
        # create new file
        try:
            repo.create_file(path, f"Add reflection {path}", content)
        except Exception:
            return False
    return True
