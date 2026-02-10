import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class Storage:
    def __init__(self):
        self.app_dir = Path.home() / ".blaaaah"
        self.app_dir.mkdir(exist_ok=True)
        self.notes_file = self.app_dir / "notes.json"
        self.prefs_file = self.app_dir / "prefs.json"
        self.reflections_file = self.app_dir / "reflections.json"

    def load_notes(self) -> Dict[str, Any]:
        if not self.notes_file.exists():
            return {"content": ""}
        return json.loads(self.notes_file.read_text())

    def save_notes(self, data: Dict[str, Any]):
        self.notes_file.write_text(json.dumps(data, indent=2))

    def load_prefs(self) -> Dict[str, Any]:
        if not self.prefs_file.exists():
            return {"days": []}
        return json.loads(self.prefs_file.read_text())

    def save_prefs(self, prefs: Dict[str, Any]):
        self.prefs_file.write_text(json.dumps(prefs, indent=2))

    def load_reflections(self):
        if not self.reflections_file.exists():
            return []
        try:
            return json.loads(self.reflections_file.read_text())
        except Exception:
            return []

    def save_reflection(self, reflection: str):
        items = self.load_reflections()
        items.append({"date": datetime.utcnow().isoformat() + "Z", "reflection": reflection})
        self.reflections_file.write_text(json.dumps(items, indent=2))
