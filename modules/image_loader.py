from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QPixmap

class ImageLoader(QObject):
    """Asynchronous image loader with memory caching."""
    
    def __init__(self):
        # We handle singleton manually at the module level
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.cache = {} # URL -> QPixmap
        
    def load(self, url, callback):
        if not url:
            return
            
        if url in self.cache:
            callback(self.cache[url])
            return
            
        request = QNetworkRequest(QUrl(url))
        reply = self.manager.get(request)
        reply.finished.connect(lambda: self._on_finished(reply, url, callback))
        
    def _on_finished(self, reply, url, callback):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.cache[url] = pixmap
            callback(pixmap)
        reply.deleteLater()

# Singleton instance
_instance = None

def get_image_loader():
    global _instance
    if _instance is None:
        _instance = ImageLoader()
    return _instance
