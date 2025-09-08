from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def apply_oled_theme(widget):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 20))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(15, 15, 25))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 50))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 170, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(20, 20, 40))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 170, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 170, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 100, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    widget.setPalette(palette)
    widget.setStyleSheet("""
        QWidget { background-color: #101014; color: #c0c0ff; }
        QPushButton { background-color: #141428; color: #00aaff; border-radius: 4px; padding: 6px; }
        QPushButton:hover { background-color: #1a1a3a; }
        QLineEdit, QTextEdit { background-color: #181828; color: #c0c0ff; border: 1px solid #00aaff; }
        QTabWidget::pane { border: 1px solid #00aaff; }
        QTabBar::tab:selected { background: #1a1a3a; color: #00aaff; }
        QTabBar::tab { background: #141428; color: #c0c0ff; }
    """)
