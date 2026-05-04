import os
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Signal

from locales import T
from widgets.download_item import DownloadItemCard

class DownloadPanel(QWidget):
    downloadRequested = Signal(str) # URL
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = {} # url -> DownloadItemCard
        
        # Load UI
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "DownloadPanel.ui")
        ui_file = QFile(ui_file_path)
        if ui_file.open(QIODevice.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            
            # Setup layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self.ui)
            
        # Connect UI
        self.ui.downloadBtn.clicked.connect(self._on_download_clicked)
        
        self.retranslate_ui()

    def retranslate_ui(self):
        self.ui.urlLabel.setText(T('url_label'))
        self.ui.urlEdit.setPlaceholderText(T('search_placeholder'))
        self.ui.downloadBtn.setText(T('download_btn'))
        self.ui.downloadAllBtn.setText(T('download_all_btn'))
        self.ui.cancelAllBtn.setText(T('cancel_all'))
        self.ui.clearListBtn.setText(T('clear_list'))
        self.ui.openFolderBtn.setText(T('st_browse'))

    def add_download_item(self, url, name=""):
        if url in self._cards:
            return
        
        card = DownloadItemCard(url, name)
        self._cards[url] = card
        self.ui.listLayout.insertWidget(0, card) # Add to top
        
    def update_item_progress(self, url, pct, speed):
        if url in self._cards:
            self._cards[url].update_progress(pct, speed)
            
    def update_item_state(self, url, state):
        if url in self._cards:
            self._cards[url].update_state(state)

    def _on_download_clicked(self):
        url = self.ui.urlEdit.text().strip()
        if url:
            self.downloadRequested.emit(url)
            self.ui.urlEdit.clear()
