from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QStackedWidget,
    QCheckBox,
    QScrollArea,
    QDialog,
    QTextBrowser,
    QMessageBox,
    QApplication,
)
from .auth import start_device_flow, poll_token_once, save_token, get_saved_token, get_client_id, save_client_id
import threading
import time


class TopBar(QWidget):
    def __init__(self, title: str, on_settings):
        super().__init__()
        h = QHBoxLayout()
        h.setContentsMargins(8, 8, 8, 8)
        icon = QLabel("icon")
        icon.setFixedWidth(40)
        h.addWidget(icon)
        h.addWidget(QLabel(title))
        h.addStretch()
        settings_btn = QPushButton("settings")
        settings_btn.clicked.connect(on_settings)
        h.addWidget(settings_btn)
        self.setLayout(h)


class WelcomeScreen(QWidget):
    def __init__(self, on_signin):
        super().__init__()
        v = QVBoxLayout()
        v.addStretch()
        label = QLabel("Welcome")
        label.setAlignment(Qt.AlignCenter)
        v.addWidget(label)
        btn = QPushButton("Sign into GitHub")
        btn.setFixedWidth(200)
        btn.clicked.connect(on_signin)
        wrapper = QWidget()
        wlayout = QHBoxLayout()
        wlayout.addStretch()
        wlayout.addWidget(btn)
        wlayout.addStretch()
        wrapper.setLayout(wlayout)
        v.addWidget(wrapper)
        v.addStretch()
        self.setLayout(v)


class EditorScreen(QWidget):
    def __init__(self, storage):
        super().__init__()
        v = QVBoxLayout()
        v.setContentsMargins(12, 12, 12, 12)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("- bullet style text editor....")
        data = storage.load_notes()
        self.editor.setPlainText(data.get("content", ""))
        self.storage = storage
        v.addWidget(self.editor)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        v.addWidget(save_btn)
        self.setLayout(v)

    def save(self):
        content = self.editor.toPlainText()
        self.storage.save_notes({"content": content})


class PasteRepoScreen(QWidget):
    def __init__(self, on_submit):
        super().__init__()
        v = QVBoxLayout()
        v.setContentsMargins(12, 12, 12, 12)
        v.addWidget(QLabel("Paste Github Repo"))
        self.input = QLineEdit()
        v.addWidget(self.input)
        submit = QPushButton("Submit")
        submit.clicked.connect(lambda: on_submit(self.input.text()))
        v.addWidget(submit)
        self.setLayout(v)


class SettingsScreen(QWidget):
    def __init__(self, storage):
        super().__init__()
        v = QVBoxLayout()
        v.setContentsMargins(12, 12, 12, 12)
        v.addWidget(QLabel("Settings"))
        
        # GitHub Client ID section
        v.addWidget(QLabel("GitHub OAuth Client ID:"))
        self.client_id_input = QLineEdit()
        client_id = get_client_id()
        if client_id:
            self.client_id_input.setText(client_id)
        self.client_id_input.setPlaceholderText("Enter your GitHub OAuth App Client ID")
        v.addWidget(self.client_id_input)
        
        v.addWidget(QLabel("select days"))
        days = ["mon", "tues", "wed", "th", "fri", "sat", "sun"]
        self.checks = {}
        h = QHBoxLayout()
        for d in days:
            cb = QCheckBox(d)
            h.addWidget(cb)
            self.checks[d] = cb
        v.addLayout(h)
        save = QPushButton("Save")
        save.clicked.connect(self.save)
        v.addWidget(save)
        self.storage = storage
        self.load()
        self.setLayout(v)

    def load(self):
        prefs = self.storage.load_prefs()
        days = prefs.get("days", [])
        for d, cb in self.checks.items():
            cb.setChecked(d in days)

    def save(self):
        days = [d for d, cb in self.checks.items() if cb.isChecked()]
        self.storage.save_prefs({"days": days})
        
        # Save GitHub Client ID if provided
        client_id = self.client_id_input.text().strip()
        if client_id:
            save_client_id(client_id)
            QMessageBox.information(self, "Success", "Settings saved successfully!")


class GitHubLoginDialog(QDialog):
    def __init__(self, client_id: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Sign In")
        self.client_id = client_id
        v = QVBoxLayout()
        self.info = QTextBrowser()
        v.addWidget(self.info)
        self.code_input = QLineEdit()
        v.addWidget(self.code_input)
        btn = QPushButton("Start Device Flow")
        btn.clicked.connect(self.start_flow)
        v.addWidget(btn)
        self.setLayout(v)
        self.device_data = None
        self.polling = False

    def start_flow(self):
        try:
            data = start_device_flow(self.client_id)
            self.device_data = data
            self.info.setPlainText(
                f"Go to {data['verification_uri']} and enter code: {data['user_code']}\n\nWaiting for authorization..."
            )
            self.polling = True
            t = threading.Thread(target=self._poll)
            t.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _poll(self):
        if not self.device_data:
            return
        device_code = self.device_data.get("device_code")
        interval = int(self.device_data.get("interval", 5))
        while self.polling:
            try:
                token_resp = poll_token_once(self.client_id, device_code)
                if token_resp.get("access_token"):
                    save_token(token_resp["access_token"])
                    self.polling = False
                    self.info.append("\nAuthorization successful. You may close this dialog.")
                    return
                elif token_resp.get("error") == "authorization_pending":
                    time.sleep(interval)
                    continue
                else:
                    self.info.append(f"\nError: {token_resp.get('error_description', token_resp.get('error'))}")
                    self.polling = False
                    return
            except Exception as e:
                self.info.append(f"\nException: {e}")
                self.polling = False
                return


class MainWindow(QMainWindow):
    def __init__(self, storage):
        super().__init__()
        self.setWindowTitle("blaaah")
        central = QWidget()
        layout = QVBoxLayout()
        self.top = TopBar("blaaah", self.show_settings)
        layout.addWidget(self.top)
        self.stack = QStackedWidget()
        self.welcome = WelcomeScreen(self.on_signin)
        self.editor = EditorScreen(storage)
        self.paste = PasteRepoScreen(self.on_paste)
        self.settings = SettingsScreen(storage)
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.editor)
        self.stack.addWidget(self.paste)
        self.stack.addWidget(self.settings)
        layout.addWidget(self.stack)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # check for existing token
        token = get_saved_token()
        if token:
            # already signed in — go to paste screen
            self.stack.setCurrentWidget(self.paste)
        else:
            self.stack.setCurrentWidget(self.welcome)

    def on_signin(self):
        # Check if client ID is configured
        client_id = get_client_id()
        if not client_id:
            QMessageBox.warning(
                self,
                "Configuration Required",
                "Please configure your GitHub OAuth Client ID in Settings first.\n\n"
                "To create a GitHub OAuth App:\n"
                "1. Go to https://github.com/settings/developers\n"
                "2. Click 'New OAuth App'\n"
                "3. Fill in the application details\n"
                "4. Copy the Client ID and paste it in Settings"
            )
            self.show_settings()
            return
        
        # open device flow dialog
        from PySide6.QtCore import Qt
        dialog = GitHubLoginDialog(client_id, parent=self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec()
        token = get_saved_token()
        if token:
            self.stack.setCurrentWidget(self.paste)

    def on_paste(self, text: str):
        # basic validation
        if "/" in text:
            self.stack.setCurrentWidget(self.editor)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings)
