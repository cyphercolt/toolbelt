from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor
import random

class ParticleSimWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sim)
        self.setMouseTracking(True)
        self.gravity = 0.2
        self.friction = 0.99
        self.sim_started = False
        # Do not start timer or spawn particles yet

    def start_sim(self):
        if not self.sim_started:
            self.spawn_particles(100)
            self.timer.start(16)
            self.sim_started = True

    def stop_sim(self):
        self.timer.stop()
        self.sim_started = False

    def showEvent(self, event):
        self.start_sim()
        super().showEvent(event)

    def hideEvent(self, event):
        self.stop_sim()
        super().hideEvent(event)

    def spawn_particles(self, n):
        for _ in range(n):
            x = random.uniform(0, self.width())
            y = random.uniform(0, self.height())
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
            color = QColor(random.randint(100,255), random.randint(100,255), random.randint(100,255))
            self.particles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'color': color})

    def update_sim(self):
        for p in self.particles:
            p['vy'] += self.gravity
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= self.friction
            p['vy'] *= self.friction
            # Bounce off walls
            if p['x'] < 0 or p['x'] > self.width():
                p['vx'] *= -1
            if p['y'] < 0 or p['y'] > self.height():
                p['vy'] *= -0.8
                p['y'] = min(max(p['y'], 0), self.height())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        for p in self.particles:
            painter.setBrush(p['color'])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(p['x']), int(p['y']), 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for _ in range(10):
                x = event.position().x()
                y = event.position().y()
                vx = random.uniform(-3, 3)
                vy = random.uniform(-3, 3)
                color = QColor(random.randint(100,255), random.randint(100,255), random.randint(100,255))
                self.particles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'color': color})

class ParticleSimTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.sim_widget = ParticleSimWidget(self)
        layout.addWidget(self.sim_widget)
        btn_row = QHBoxLayout()
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self.reset_particles)
        btn_row.addWidget(reset_btn)
        info = QLabel('Click to spawn more particles!')
        btn_row.addWidget(info)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def reset_particles(self):
        self.sim_widget.particles.clear()
        self.sim_widget.spawn_particles(100)
