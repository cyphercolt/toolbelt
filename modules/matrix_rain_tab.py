from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QFont
import random
from modules.particle_sim_tab import ParticleSimTab

class MatrixRainWidget(QWidget):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rain)
        self.apply_settings(settings or {})
        self.columns = []
        self.column_ages = []
        self.init_columns()
        self.timer.start(self.settings.get('speed', 50))

    def apply_settings(self, settings):
        self.settings = settings
        self.font_size = self.settings.get('font_size', 18)
        self.min_strand_length = self.settings.get('min_strand_length', 8)
        self.max_strand_length = self.settings.get('max_strand_length', 20)
        self.strand_lifetime = self.settings.get('strand_lifetime', 100)
        self.chars = self.settings.get('chars', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*')
        self.bg_color = self.settings.get('bg_color', (0, 0, 0))
        self.setFont(QFont('Consolas', self.font_size, QFont.Weight.Bold))

    def init_columns(self):
        width = self.width()
        self.n_cols = width // self.font_size
        # Each column gets a random strand length between min and max
        self.strand_lengths = [random.randint(self.min_strand_length, self.max_strand_length) for _ in range(self.n_cols)]
        self.max_strand_height = (self.height() // self.font_size) + max(self.strand_lengths or [self.max_strand_length])
        self.columns = [random.randint(0, self.max_strand_height) for _ in range(self.n_cols)]
        self.column_ages = [0 for _ in range(self.n_cols)]

    def resizeEvent(self, event):
        self.init_columns()
        super().resizeEvent(event)

    def update_rain(self):
        for i in range(len(self.columns)):
            if self.column_ages[i] >= self.strand_lifetime or self.columns[i] > self.max_strand_height:
                self.columns[i] = 0
                self.column_ages[i] = 0
                # Pick a new random strand length for this column
                self.strand_lengths[i] = random.randint(self.min_strand_length, self.max_strand_length)
            else:
                if random.random() > 0.975:
                    self.columns[i] = 0
                    self.column_ages[i] = 0
                    self.strand_lengths[i] = random.randint(self.min_strand_length, self.max_strand_length)
                else:
                    self.columns[i] += 1
                    self.column_ages[i] += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(*self.bg_color))
        painter.setFont(self.font())
        for i, y in enumerate(self.columns):
            x = i * self.font_size
            strand_len = self.strand_lengths[i] if hasattr(self, 'strand_lengths') else self.max_strand_length
            for idx, j in enumerate(range(max(0, y - strand_len), y)):
                if j * self.font_size > self.height():
                    continue
                char = random.choice(self.chars)
                pos_in_strand = y - j - 1  # 0 is head, increasing toward tail
                if pos_in_strand == 0:
                    painter.setPen(QColor(180, 255, 180))
                else:
                    alpha = max(0, int(255 * (1 - pos_in_strand / max(1, strand_len-1))))
                    painter.setPen(QColor(0, 255, 70, alpha))
                painter.drawText(x, j * self.font_size, self.font_size, self.font_size, Qt.AlignmentFlag.AlignCenter, char)

class MatrixRainTab(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        self.main_window = main_window
        layout = QVBoxLayout()
        row = QHBoxLayout()
        self.start_btn = QPushButton('Start Matrix Rain')
        self.start_btn.clicked.connect(self.launch_matrix_rain)
        row.addWidget(self.start_btn)
        self.settings_btn = QPushButton('⚙️')
        self.settings_btn.setToolTip('Matrix Rain Settings')
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet('font-size: 20px; background: #232b36; color: #7ecfff; border-radius: 18px;')
        self.settings_btn.clicked.connect(self.open_matrix_rain_settings)
        row.addWidget(self.settings_btn)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(1)
        self.setLayout(layout)

    def open_matrix_rain_settings(self):
        from modules.matrix_rain_settings import MatrixRainSettingsDialog
        dlg = MatrixRainSettingsDialog(self, settings=getattr(self, 'matrix_rain_settings', None))
        if dlg.exec():
            self.matrix_rain_settings = dlg.get_settings()
            if 'strand_lifetime' not in self.matrix_rain_settings:
                self.matrix_rain_settings['strand_lifetime'] = 100

    def launch_matrix_rain(self):
        if self.main_window is not None:
            settings = getattr(self, 'matrix_rain_settings', None)
            self.overlay = MatrixRainOverlay(self.main_window, settings=settings)
            self.overlay.show()

class FunToolsTab(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QTabWidget, QVBoxLayout
        self.main_window = main_window
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        # Matrix Rain tab (now a control tab, not animation)
        from modules.matrix_rain_tab import MatrixRainTab
        self.matrix_rain_tab = MatrixRainTab(self, main_window=main_window)
        self.tabs.addTab(self.matrix_rain_tab, "Matrix Rain")
        # Particle Sim tab
        self.particle_sim_tab = ParticleSimTab(self)
        self.tabs.addTab(self.particle_sim_tab, "Particle Sim")
        layout.addWidget(self.tabs)
        self.setLayout(layout)

class MatrixRainOverlay(MatrixRainWidget):
    def __init__(self, main_window, settings=None):
        super().__init__(None, settings=settings)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        geo = main_window.frameGeometry()
        self.setGeometry(geo)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.close()
