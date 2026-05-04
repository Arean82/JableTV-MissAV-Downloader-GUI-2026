import os
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Signal, Qt
from PySide6.QtGui import QPixmap

from locales import T
from modules.image_loader import get_image_loader

class VideoThumbnailCard(QWidget):
    doubleClicked = Signal(str) # URL
    selectionChanged = Signal(bool, str) # Selected, URL
    
    def __init__(self, url, title, thumb_url=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.title = title
        
        # Load UI
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "VideoThumbnailCard.ui")
        ui_file = QFile(ui_file_path)
        if ui_file.open(QIODevice.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            
            # Setup layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self.ui)
            
        self.ui.titleLabel.setText(title)
        self.ui.selectCheck.stateChanged.connect(self._on_check_changed)
        
        # Async Thumbnail
        if thumb_url:
            get_image_loader().load(thumb_url, self.set_thumbnail)
            
        self.retranslate_ui()

    def retranslate_ui(self):
        self.ui.selectCheck.setText(T('select'))

    def set_thumbnail(self, pixmap):
        self.ui.thumbLabel.setPixmap(pixmap)

    def is_selected(self):
        return self.ui.selectCheck.isChecked()

    def set_selected(self, selected):
        self.ui.selectCheck.setChecked(selected)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.url)

    def _on_check_changed(self, state):
        self.selectionChanged.emit(state == Qt.Checked, self.url)
