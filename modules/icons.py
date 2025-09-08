from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

def cpu_icon():
    label = QLabel()
    label.setPixmap(QPixmap(32, 32))
    label.setStyleSheet('background: none;')
    label.setText('🖥️')
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label

def ram_icon():
    label = QLabel()
    label.setPixmap(QPixmap(32, 32))
    label.setStyleSheet('background: none;')
    label.setText('💾')
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label

def disk_icon():
    label = QLabel()
    label.setPixmap(QPixmap(32, 32))
    label.setStyleSheet('background: none;')
    label.setText('🗄️')
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label

def battery_icon():
    label = QLabel()
    label.setPixmap(QPixmap(32, 32))
    label.setStyleSheet('background: none;')
    label.setText('🔋')
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label
