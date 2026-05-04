import os
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Signal

from locales import T

class DownloadItemCard(QWidget):
    cancelClicked = Signal(str) # Emits URL
    
    def __init__(self, url, name="", parent=None):
        super().__init__(parent)
        self.url = url
        
        # Load UI
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "DownloadItem.ui")
        ui_file = QFile(ui_file_path)
        if ui_file.open(QIODevice.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            
            # Setup layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self.ui)
            
        self.ui.nameLabel.setText(name or url)
        self.ui.cancelBtn.clicked.connect(lambda: self.cancelClicked.emit(self.url))
        self.retranslate_ui()

    def retranslate_ui(self):
        # We don't translate the name or speed, but we can translate "Waiting" if it's static
        pass

    def update_progress(self, pct, speed):
        self.ui.progressBar.setValue(pct)
        self.ui.speedLabel.setText(speed)
        
    def update_state(self, state):
        # Map internal state to translated state
        state_map = {
            '下載中': T('state_downloading'),
            '等待中': T('state_waiting'),
            '已下載': T('state_downloaded'),
            '已取消': T('state_cancelled'),
            '錯誤': T('state_error'),
            '合併中': T('state_merging')
        }
        self.ui.statusLabel.setText(state_map.get(state, state))
        
        # Update colors based on state if needed
        if state == '已下載':
            self.ui.statusLabel.setStyleSheet("color: #4ade80;") # Green
        elif state == '錯誤':
            self.ui.statusLabel.setStyleSheet("color: #f87171;") # Red
        else:
            self.ui.statusLabel.setStyleSheet("color: #9494b4;")
