import os
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Signal

from locales import T, get_lang, set_lang
from modules.config_manager import get_config

class SettingsPanel(QWidget):
    languageChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load UI
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "SettingsPanel.ui")
        ui_file = QFile(ui_file_path)
        if ui_file.open(QIODevice.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            
            # Setup layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self.ui)
        
        # Populate combos
        self.config = get_config()
        self._setup_combos()
        
        # Load initial values
        self.ui.destEdit.setText(self.config.get("save_path"))
        
        # Connect signals
        self.ui.browseBtn.clicked.connect(self._on_browse)
        self.ui.langCombo.currentIndexChanged.connect(self._on_lang_changed)
        
        # Save on change
        self.ui.destEdit.textChanged.connect(lambda t: self.config.set("save_path", t))
        
        self.retranslate_ui()
        self._set_combo_values()

    def _setup_combos(self):
        # Speed
        self.ui.speedCombo.addItems([T('unlimited'), '1 MB/s', '2 MB/s', '5 MB/s', '10 MB/s', '15 MB/s'])
        # Concurrent
        self.ui.concCombo.addItems([str(i) for i in range(1, 11)])
        # Resolution
        self.ui.resCombo.addItems([T('resolution_highest'), T('resolution_lowest')])
        # Language
        self.ui.langCombo.addItems(['繁體中文', 'English'])

        # Connect combo saves
        self.ui.concCombo.currentIndexChanged.connect(lambda i: self.config.set("max_concurrent", int(self.ui.concCombo.itemText(i))))
        self.ui.resCombo.currentIndexChanged.connect(lambda i: self.config.set("resolution", "highest" if i == 0 else "lowest"))

    def _set_combo_values(self):
        # Sync combos with config data
        conc = str(self.config.get("max_concurrent"))
        idx = self.ui.concCombo.findText(conc)
        if idx >= 0: self.ui.concCombo.setCurrentIndex(idx)
        
        self.ui.resCombo.setCurrentIndex(0 if self.config.get("resolution") == "highest" else 1)
        self.ui.langCombo.setCurrentIndex(0 if get_lang() == 'zh' else 1)

    def retranslate_ui(self):
        self.ui.downloadGroup.setTitle(T('download_settings'))
        self.ui.destLabel.setText(T('save_location_setting'))
        self.ui.browseBtn.setText(T('browse_folder'))
        self.ui.speedLabel.setText(T('speed_limit_setting'))
        self.ui.concLabel.setText(T('concurrent_setting'))
        self.ui.resLabel.setText(T('resolution_setting'))
        self.ui.interfaceGroup.setTitle(T('settings_title'))
        self.ui.langLabel.setText(T('language_setting'))

    def _on_browse(self):
        dir = QFileDialog.getExistingDirectory(self, T('save_location_setting'))
        if dir:
            self.ui.destEdit.setText(dir)

    def _on_lang_changed(self, index):
        new_lang = 'zh' if index == 0 else 'en'
        if new_lang != get_lang():
            set_lang(new_lang)
            self.config.set("language", new_lang)
            self.languageChanged.emit(new_lang)
            self.retranslate_ui()
