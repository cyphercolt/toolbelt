from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import socket
import time
import subprocess

class PortScanWorker(QThread):
    result = pyqtSignal(bool, float)
    def __init__(self, host, port, timeout=10):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
    def run(self):
        start = time.time()
        is_open = False
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout):
                is_open = True
        except Exception:
            is_open = False
        elapsed = (time.time() - start) * 1000
        self.result.emit(is_open, elapsed)

class PingWorker(QThread):
    result = pyqtSignal(float)
    def __init__(self, host):
        super().__init__()
        self.host = host
    def run(self):
        try:
            # Windows ping: -n 1, Linux/Mac: -c 1
            count_flag = '-n' if socket.gethostname().find('.') == -1 else '-c'
            proc = subprocess.run(['ping', count_flag, '1', self.host], capture_output=True, text=True, timeout=5)
            output = proc.stdout
            # Parse ms from output
            import re
            match = re.search(r'([0-9]+(?:\.[0-9]+)?) ?ms', output)
            if match:
                ms = float(match.group(1))
            else:
                ms = -1
        except Exception:
            ms = -1
        self.result.emit(ms)

class PortScannerTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QGroupBox, QProgressBar
        layout = QVBoxLayout()
        # Card-style group for input
        input_group = QGroupBox("Port Scan")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; border-radius: 8px; margin-top: 10px; padding: 10px; border: 1px solid #444; } ")
        input_layout = QHBoxLayout()
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('e.g. 8.8.8.8 or example.com')
        self.host_input.setMinimumWidth(180)
        input_layout.addWidget(QLabel('Host/IP:'))
        input_layout.addWidget(self.host_input)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        input_layout.addWidget(QLabel('Port:'))
        input_layout.addWidget(self.port_input)
        self.scan_btn = QPushButton('Scan')
        self.scan_btn.setStyleSheet("padding: 6px 18px; font-weight: bold;")
        self.scan_btn.clicked.connect(self.start_scan)
        input_layout.addWidget(self.scan_btn)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        # Status label with icon
        self.status_label = QLabel('Enter host and port, then click Scan.')
        self.status_label.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px; background: #232b36; color: #fff;")
        layout.addWidget(self.status_label)
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        # Ping label
        self.ping_label = QLabel('Ping: - ms')
        self.ping_label.setStyleSheet("font-size: 14px; color: #7ecfff; padding: 4px;")
        layout.addWidget(self.ping_label)
        layout.addStretch(1)
        self.setLayout(layout)
        self.worker = None
        self.ping_worker = None
    def start_scan(self):
        host = self.host_input.text().strip()
        port = self.port_input.value()
        if not host:
            self.status_label.setText('Please enter a host or IP.')
            self.status_label.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px; background: #232b36; color: #fff;")
            return
        self.status_label.setText('Scanning...')
        self.status_label.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px; background: #232b36; color: #fff;")
        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.worker = PortScanWorker(host, port)
        self.worker.result.connect(self.on_scan_result)
        self.worker.start()
        self.ping_label.setText('Pinging...')
        self.ping_worker = PingWorker(host)
        self.ping_worker.result.connect(self.on_ping_result)
        self.ping_worker.start()
    def on_scan_result(self, is_open, elapsed):
        if is_open:
            self.status_label.setText(f'🟢 Port is <b>OPEN</b> ({elapsed:.1f} ms)')
            self.status_label.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px; background: #1e3a1e; color: #aaffaa; border: 1px solid #3c6; font-weight: bold;")
        else:
            self.status_label.setText(f'🔴 Port is <b>CLOSED</b> or unreachable ({elapsed:.1f} ms)')
            self.status_label.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 6px; background: #3a1e1e; color: #ffaaaa; border: 1px solid #c66; font-weight: bold;")
        self.scan_btn.setEnabled(True)
        self.progress.setVisible(False)
    def on_ping_result(self, ms):
        if ms >= 0:
            self.ping_label.setText(f'Ping: {ms:.1f} ms')
        else:
            self.ping_label.setText('Ping: timeout or unreachable')
