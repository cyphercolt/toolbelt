from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QLineEdit, QPushButton, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class MatrixRainSettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Matrix Rain Settings")
        self.setModal(True)
        self.settings = settings or {}
        layout = QVBoxLayout()

        # Background Color
        bg_row = QHBoxLayout()
        bg_row.addWidget(QLabel("Background Color:"))
        self.bg_r_spin = QSpinBox()
        self.bg_r_spin.setRange(0, 255)
        self.bg_g_spin = QSpinBox()
        self.bg_g_spin.setRange(0, 255)
        self.bg_b_spin = QSpinBox()
        self.bg_b_spin.setRange(0, 255)
        bg_color = self.settings.get('bg_color', (0, 0, 0))
        self.bg_r_spin.setValue(bg_color[0])
        self.bg_g_spin.setValue(bg_color[1])
        self.bg_b_spin.setValue(bg_color[2])
        self.bg_hex_edit = QLineEdit()
        self.bg_hex_edit.setMaxLength(7)
        self.bg_hex_edit.setFixedWidth(70)
        self.bg_hex_edit.setText('#%02x%02x%02x' % bg_color)
        bg_row.addWidget(QLabel('R:'))
        bg_row.addWidget(self.bg_r_spin)
        bg_row.addWidget(QLabel('G:'))
        bg_row.addWidget(self.bg_g_spin)
        bg_row.addWidget(QLabel('B:'))
        bg_row.addWidget(self.bg_b_spin)
        bg_row.addWidget(QLabel('Hex:'))
        bg_row.addWidget(self.bg_hex_edit)
        # Add color picker button
        self.bg_color_btn = QPushButton('Pick Color')
        bg_row.addWidget(self.bg_color_btn)
        layout.addLayout(bg_row)

        # Sync RGB <-> Hex
        def update_hex():
            r = self.bg_r_spin.value()
            g = self.bg_g_spin.value()
            b = self.bg_b_spin.value()
            self.bg_hex_edit.setText('#%02x%02x%02x' % (r, g, b))
        def update_rgb():
            text = self.bg_hex_edit.text().lstrip('#')
            if len(text) == 6:
                try:
                    r = int(text[0:2], 16)
                    g = int(text[2:4], 16)
                    b = int(text[4:6], 16)
                    self.bg_r_spin.setValue(r)
                    self.bg_g_spin.setValue(g)
                    self.bg_b_spin.setValue(b)
                except ValueError:
                    pass
        def update_from_picker():
            color = QColorDialog.getColor(
                QColor(self.bg_r_spin.value(), self.bg_g_spin.value(), self.bg_b_spin.value()),
                self, 'Select Background Color')
            if color.isValid():
                self.bg_r_spin.setValue(color.red())
                self.bg_g_spin.setValue(color.green())
                self.bg_b_spin.setValue(color.blue())
        self.bg_r_spin.valueChanged.connect(update_hex)
        self.bg_g_spin.valueChanged.connect(update_hex)
        self.bg_b_spin.valueChanged.connect(update_hex)
        self.bg_hex_edit.textChanged.connect(update_rgb)
        self.bg_color_btn.clicked.connect(update_from_picker)

        # Font size
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(self.settings.get('font_size', 18))
        font_row.addWidget(self.font_size_spin)
        layout.addLayout(font_row)

        # Speed
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed (ms):"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(10, 500)
        self.speed_spin.setValue(self.settings.get('speed', 50))
        speed_row.addWidget(self.speed_spin)
        layout.addLayout(speed_row)

        # Strand Length (min/max)
        strand_len_row = QHBoxLayout()
        strand_len_row.addWidget(QLabel("Min Strand Length (chars):"))
        self.strand_min_spin = QSpinBox()
        self.strand_min_spin.setRange(2, 100)
        self.strand_min_spin.setValue(self.settings.get('min_strand_length', 8))
        strand_len_row.addWidget(self.strand_min_spin)
        strand_len_row.addWidget(QLabel("Max Strand Length (chars):"))
        self.strand_max_spin = QSpinBox()
        self.strand_max_spin.setRange(2, 100)
        self.strand_max_spin.setValue(self.settings.get('max_strand_length', 20))
        strand_len_row.addWidget(self.strand_max_spin)
        layout.addLayout(strand_len_row)

        # Strand Lifetime
        strand_row = QHBoxLayout()
        strand_row.addWidget(QLabel("Strand Lifetime (frames):"))
        self.strand_spin = QSpinBox()
        self.strand_spin.setRange(10, 500)
        self.strand_spin.setValue(self.settings.get('strand_lifetime', 100))
        strand_row.addWidget(self.strand_spin)
        layout.addLayout(strand_row)

        # Characters
        chars_row = QHBoxLayout()
        chars_row.addWidget(QLabel("Characters:"))
        self.chars_edit = QLineEdit()
        self.chars_edit.setText(self.settings.get('chars', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*'))
        chars_row.addWidget(self.chars_edit)
        layout.addLayout(chars_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_settings(self):
        return {
            'font_size': self.font_size_spin.value(),
            'speed': self.speed_spin.value(),
            'min_strand_length': self.strand_min_spin.value(),
            'max_strand_length': self.strand_max_spin.value(),
            'strand_lifetime': self.strand_spin.value(),
            'chars': self.chars_edit.text(),
            'bg_color': (
                self.bg_r_spin.value(),
                self.bg_g_spin.value(),
                self.bg_b_spin.value()
            ),
        }
