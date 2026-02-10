import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication

from .ui import MainWindow
from .storage import Storage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from .gemma import rewrite_notes
from .github_push import push_reflection


def _generate_and_save_reflection(storage: Storage):
    # load notes and prefs
    notes = storage.load_notes().get("content", "")
    prefs = storage.load_prefs()
    days = prefs.get("days", [])
    # check if today is selected
    today = datetime.datetime.now().strftime("%a").lower()
    # map mon,tues,wed etc to first three letters used by strftime
    mapping = {"mon": "mon", "tues": "tue", "wed": "wed", "thu": "thu", "fri": "fri", "sat": "sat", "sun": "sun"}
    today_key = today[:3]
    ok = False
    for k in days:
        if k.startswith(today_key):
            ok = True
            break
    if not ok:
        return
    # generate
    reflection = rewrite_notes(notes)
    if reflection:
        storage.save_reflection(reflection)
        # optionally push to GitHub
        repo = prefs.get("push_repo")
        if repo:
            # filename like 2026-02-10.md
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            path = f"reflections/{date_str}.md"
            push_reflection(repo, path, reflection)


class BlaaahApp:
    def __init__(self):
        self.app = QApplication([])
        self.storage = Storage()
        self.window: Optional[MainWindow] = None
        self.scheduler = BackgroundScheduler()
        # schedule 5pm daily; job checks prefs to see if today is enabled
        trigger = CronTrigger(hour=17, minute=0)
        self.scheduler.add_job(lambda: _generate_and_save_reflection(self.storage), trigger=trigger, id="daily_reflection")
        self.scheduler.start()

    def run(self):
        self.window = MainWindow(self.storage)
        self.window.show()
        try:
            import sys
            sys.exit(self.app.exec())
        finally:
            self.scheduler.shutdown()


# keep previous module-level main for direct runs
if __name__ == "__main__":
    app = BlaaahApp()
    app.run()
