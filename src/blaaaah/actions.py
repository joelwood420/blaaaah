from typing import Optional
import datetime

from .gemma import rewrite_notes
from .github_push import push_reflection
from .storage import Storage


def generate_and_save(storage: Storage, push: bool = True) -> Optional[dict]:
    """Generate a reflection from stored notes, save it locally, and optionally push to GitHub.

    Returns a dict with keys: reflection (str), pushed (bool), repo (str|None)
    or None on failure.
    """
    notes = storage.load_notes().get("content", "")
    if not notes.strip():
        return None
    reflection = rewrite_notes(notes)
    if not reflection:
        return None
    storage.save_reflection(reflection)
    prefs = storage.load_prefs()
    repo = prefs.get("push_repo")
    pushed = False
    if push and repo:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        path = f"reflections/{date_str}.md"
        pushed = push_reflection(repo, path, reflection)
    return {"reflection": reflection, "pushed": pushed, "repo": repo}


def simulate_5pm(storage: Storage, push: bool = True, force: bool = False) -> Optional[dict]:
    """Simulate the scheduled 5pm job:
    - Checks prefs for selected days (unless force=True)
    - Generates reflection, saves it, optionally pushes
    - Clears the notes (saves empty content)
    Returns same dict as generate_and_save or None.
    """
    prefs = storage.load_prefs()
    days = prefs.get("days", [])
    if not force:
        # determine today key like 'mon','tues', etc
        today = datetime.datetime.now().strftime("%a").lower()
        today_key = today[:3]
        ok = False
        for k in days:
            if k.startswith(today_key):
                ok = True
                break
        if not ok:
            return None
    # generate and save
    res = generate_and_save(storage, push=push)
    if res:
        # clear notes
        try:
            storage.save_notes({"content": ""})
        except Exception:
            pass
    return res
