from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor

class LoadingSpinner(QWidget):
    """A custom rotating spinner widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(10) # Smooth 100fps rotation
        self.setFixedSize(60, 60)
        self.hide() # Hidden by default

    def _rotate(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Color based on parent's text color (roughly)
        color = QColor("#e94560") # Accent color
        
        pen = QPen(color)
        pen.setWidth(5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw a 270-degree arc
        rect = QRectF(5, 5, 50, 50)
        painter.drawArc(rect, self.angle * 16, 270 * 16)
