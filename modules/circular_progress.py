from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

class CircularProgress(QWidget):
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.value = 0
        self.label = label
        self.color = color
        self.setMinimumSize(120, 120)
        self.thickness = 14
        self.font_size = 18

    def setValue(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(10, 10, self.width()-20, self.height()-20)
        # Draw background circle
        pen = QPen(QColor(40, 40, 40), getattr(self, 'thickness', 14))
        painter.setPen(pen)
        painter.drawEllipse(rect)
        # Draw progress arc
        pen = QPen(self.color, getattr(self, 'thickness', 14))
        painter.setPen(pen)
        span_angle = int(360 * 16 * self.value / 100)
        painter.drawArc(rect, -90*16, -span_angle)
        # Draw text
        painter.setPen(QColor(220, 220, 220))
        painter.setFont(QFont('Consolas', getattr(self, 'font_size', 18), QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%\n{self.label}")
