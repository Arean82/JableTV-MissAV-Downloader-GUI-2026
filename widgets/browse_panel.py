import os
from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Signal, Qt

from locales import T
from widgets.video_thumbnail_card import VideoThumbnailCard
from modules.scraper import ScraperThread
from widgets.loading_spinner import LoadingSpinner

class BrowsePanel(QWidget):
    downloadRequested = Signal(list) # List of URLs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = []
        self._grid_layout = None
        
        # Load UI
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..", "ui", "BrowsePanel.ui")
        ui_file = QFile(ui_file_path)
        if ui_file.open(QIODevice.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            
            # Setup container layout
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self.ui)
        
        # Initialize Grid
        self._grid_layout = QGridLayout()
        self._grid_layout.setSpacing(15)
        self._grid_layout.setContentsMargins(20, 20, 20, 20)
        self.ui.listLayout.addLayout(self._grid_layout)
        self.ui.listLayout.addStretch() # Push everything to top
        
        # Spinner
        self.spinner = LoadingSpinner(self.ui.scrollAreaWidgetContents)
        # Position it in the middle of the scroll area
        
        # Connect signals
        self.ui.downloadSelectedBtn.clicked.connect(self._on_download_selected)
        self.ui.searchBtn.clicked.connect(self._on_search_clicked)
        
        self.retranslate_ui()
        # Load initial content
        self._load_url("https://jable.tv/hot/")

    def _load_url(self, url):
        self.clear_grid()
        self.spinner.show()
        # Center the spinner
        self._scraper_thread = ScraperThread(url)
        self._scraper_thread.finished.connect(self._on_videos_loaded)
        self._scraper_thread.start()
        
    def _on_videos_loaded(self, videos):
        self.spinner.hide()
        for v in videos:
            self.add_video(v['url'], v['title'], v['thumb'])
            
    def _on_search_clicked(self):
        query = self.ui.searchEdit.text().strip()
        if query:
            # Simple search URL for demonstration; real logic should use search_videos
            self._load_url(f"https://jable.tv/search/{query}/")

    def retranslate_ui(self):
        self.ui.catLabel.setText(T('category_label'))
        self.ui.searchEdit.setPlaceholderText(T('search_placeholder'))
        self.ui.searchBtn.setText(T('search_btn'))
        self.ui.downloadSelectedBtn.setText(T('download_selected'))
        self.ui.prevBtn.setText(T('prev_page'))
        self.ui.nextBtn.setText(T('next_page'))

    def clear_grid(self):
        # Clear existing cards
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._cards.clear()

    def add_video(self, url, title, thumb_url=None):
        card = VideoThumbnailCard(url, title, thumb_url)
        self._cards.append(card)
        self._relayout_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout_grid()
        
        # Center the spinner
        self.spinner.move(
            (self.ui.scrollArea.width() - self.spinner.width()) // 2,
            (self.ui.scrollArea.height() - self.spinner.height()) // 2
        )

    def _relayout_grid(self):
        if not self._cards or not self._grid_layout:
            return
            
        # Calculate columns based on width
        width = self.ui.scrollArea.width() - 40 # accounting for margins
        col_width = 235 # card width (220) + spacing (15)
        cols = max(1, width // col_width)
        
        # Remove all from grid without deleting
        for i in reversed(range(self._grid_layout.count())):
            self._grid_layout.takeAt(i)
            
        # Re-add to grid
        for i, card in enumerate(self._cards):
            row = i // cols
            col = i % cols
            self._grid_layout.addWidget(card, row, col)

    def _on_download_selected(self):
        urls = [card.url for card in self._cards if card.is_selected()]
        if urls:
            self.downloadRequested.emit(urls)
