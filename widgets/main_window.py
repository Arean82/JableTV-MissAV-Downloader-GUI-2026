import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QAction

from locales import T, get_lang, set_lang
from modules.downloader import DownloadManager
from modules.themes import Themes
from modules.config_manager import get_config

class MainWindow(QMainWindow):
    def __init__(self, url="", dest=None, lang=None):
        super().__init__()
        self.config = get_config()
        
        # Logic - prioritize args, then config
        self.dest = dest if dest else self.config.get("save_path")
        init_lang = lang if lang else self.config.get("language")
        self._is_dark = (self.config.get("theme") == "dark")
        
        # Initialize translation system
        set_lang(init_lang)
        
        self.dlmgr = DownloadManager()
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "MainWindow.ui")
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
            sys.exit(-1)
        
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Add sub-panels
        from widgets.download_panel import DownloadPanel
        self.download_panel = DownloadPanel(self.ui.tabDownload)
        from PySide6.QtWidgets import QVBoxLayout, QStatusBar
        download_layout = QVBoxLayout(self.ui.tabDownload)
        download_layout.setContentsMargins(0,0,0,0)
        download_layout.addWidget(self.download_panel)

        from widgets.browse_panel import BrowsePanel
        self.browse_panel = BrowsePanel(self.ui.tabBrowse)
        browse_layout = QVBoxLayout(self.ui.tabBrowse)
        browse_layout.setContentsMargins(0,0,0,0)
        browse_layout.addWidget(self.browse_panel)
        
        # Menu Bar
        self._setup_menu_bar()
        self.menubar.setNativeMenuBar(True) # Force native OS integration
        self.menubar.setStyleSheet("")       # Explicitly clear any styling
        
        # Status Bar (Manual since ui is now QWidget)
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet("")     # Explicitly clear any styling
        self.setStatusBar(self.statusbar)
        
        # Set central widget
        self.setCentralWidget(self.ui)
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        
        # Initial State
        set_lang(lang)
        self.retranslate_ui()
        
        # Signals
        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)
        self.download_panel.downloadRequested.connect(self._on_download_requested)
        self.browse_panel.downloadRequested.connect(self._on_multi_download_requested)
        
        # Connect Download Manager
        self.dlmgr.stateChanged.connect(self.download_panel.update_item_state)
        self.dlmgr.progressUpdated.connect(self.download_panel.update_item_progress)
        self.dlmgr.listChanged.connect(self._on_dl_list_changed)
        
        # Clipboard Listener
        self._last_clipboard = ""
        QGuiApplication.clipboard().dataChanged.connect(self._on_clipboard_changed)
        
        # Load existing data
        self.dlmgr.load_csv("JableTV.csv")
        self._on_dl_list_changed()
        
        # Apply Theme
        self.toggle_theme() # Sets initial dark theme

    def _setup_menu_bar(self):
        self.menubar = self.menuBar()
        
        # File Menu
        self.menuFile = self.menubar.addMenu("File")
        self.actionExit = QAction("Exit", self)
        self.actionExit.triggered.connect(self.close)
        self.menuFile.addAction(self.actionExit)
        
        # View Menu
        self.menuView = self.menubar.addMenu("View")
        self.actionSettings = QAction("Settings", self)
        self.actionSettings.triggered.connect(self._show_settings)
        self.menuView.addAction(self.actionSettings)
        
        self.actionToggleTheme = QAction("Toggle Dark/Light Mode", self)
        self.actionToggleTheme.triggered.connect(self.toggle_theme)
        self.menuView.addAction(self.actionToggleTheme)
        
        # Help Menu
        self.menuHelp = self.menubar.addMenu("Help")
        self.actionAbout = QAction("About", self)
        self.menuHelp.addAction(self.actionAbout)

    def toggle_theme(self):
        self._is_dark = not self._is_dark
        self.config.set("theme", "dark" if self._is_dark else "light")
        
        qss = Themes.DARK if self._is_dark else Themes.LIGHT
        
        # Apply theme to the container widget that holds all tabs
        # This restores the "Browser" background while sparing the QMainWindow shell
        self.ui.tabWidget.setStyleSheet(qss)
        
        self.statusbar.showMessage(f"Theme switched to {'Dark' if self._is_dark else 'Light'}", 2000)

    def _show_settings(self):
        from widgets.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.settings_panel.languageChanged.connect(self.retranslate_ui)
        dialog.exec()

    def retranslate_ui(self):
        """Update all text from locales.py"""
        self.ui.tabWidget.setTabText(0, T('tab_browse'))
        self.ui.tabWidget.setTabText(1, T('tab_download'))
        
        # Menus
        self.menuFile.setTitle(T('menu_file'))
        self.actionExit.setText(T('menu_exit'))
        self.menuView.setTitle(T('menu_view'))
        self.actionSettings.setText(T('tab_settings'))
        self.actionToggleTheme.setText(T('menu_toggle_theme'))
        self.menuHelp.setTitle(T('menu_help'))
        self.actionAbout.setText(T('menu_about'))
        
        self.download_panel.retranslate_ui()
        self.browse_panel.retranslate_ui()
        
        self.statusbar.showMessage(T('st_idle'))

    def _on_tab_changed(self, index):
        # Placeholder for tab-specific logic
        pass

    def _on_dl_list_changed(self):
        items = self.dlmgr.get_items()
        for item in items:
            self.download_panel.add_download_item(item.url, item.name)
            self.download_panel.update_item_state(item.url, item.state)
            self.download_panel.update_item_progress(item.url, item.progress, item.speed)

    def _on_download_requested(self, url):
        self.dlmgr.add_item(url)
        self.dlmgr.enqueue(url, self.dest)

    def _on_multi_download_requested(self, urls):
        for url in urls:
            self.dlmgr.add_item(url)
            self.dlmgr.enqueue(url, self.dest)
        self.ui.tabWidget.setCurrentIndex(1) # Switch to download tab

    def _on_clipboard_changed(self):
        text = QGuiApplication.clipboard().text().strip()
        if text == self._last_clipboard:
            return
        self._last_clipboard = text
        
        # Validate if it's a supported URL
        import M3U8Sites
        if M3U8Sites.VaildateUrl(text):
            self.download_panel.ui.urlEdit.setText(text)
            self.statusbar.showMessage(f"URL detected: {text}", 5000)

if __name__ == "__main__":
    # Test runner
    app = QApplication(sys.argv)
    window = MainWindow(lang="en")
    window.show()
    sys.exit(app.exec())
