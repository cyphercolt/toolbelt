from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class ScanlineOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(parent.size())
        parent.installEventFilter(self)
        self.show()
        # Animation for moving scanline
        from PyQt6.QtCore import QTimer
        self._scanline_pos = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._move_scanline)
        self._timer.start(30)  # 30 ms for smooth animation
        self._frame = 0

    def _move_scanline(self):
        self._frame += 1
        if self._frame % 4 == 0:  # Move every 4 frames for slower movement
            self._scanline_pos = (self._scanline_pos + 2) % self.height()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw static dark scanlines
        painter.setOpacity(0.25)
        color = QColor(0, 0, 0)
        h = self.height()
        for y in range(0, h, 4):
            painter.fillRect(0, y, self.width(), 2, color)
        # Draw moving bright scanline
        painter.setOpacity(0.5)
        bright = QColor(120, 255, 120, 180)
        painter.fillRect(0, self._scanline_pos, self.width(), 2, bright)
        painter.end()

    def eventFilter(self, obj, event):
        # Always match the viewport's size and position
        if event.type() == event.Type.Resize:
            self.resize(obj.size())
        elif event.type() == event.Type.Paint or event.type() == event.Type.Wheel or event.type() == event.Type.Scroll:
            # On scroll or paint, reposition to (0,0) and resize to viewport
            self.move(0, 0)
            self.resize(obj.size())
        return False
