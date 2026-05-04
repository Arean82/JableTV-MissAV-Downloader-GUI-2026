from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from widgets.settings_panel import SettingsPanel
from locales import T

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T('settings_title'))
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        self.settings_panel = SettingsPanel(self)
        layout.addWidget(self.settings_panel)
        
        # Add OK button
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)
        
        # Connect language change signal if needed
        self.settings_panel.languageChanged.connect(self._on_lang_changed)

    def _on_lang_changed(self, lang):
        self.setWindowTitle(T('settings_title'))
        # The parent (MainWindow) handles its own retranslation via signals
