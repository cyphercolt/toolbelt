from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QSpacerItem, QFrame, QProgressBar
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
import platform, os, psutil
from modules.circular_progress import CircularProgress

# Try to get a better CPU name on Windows
import sys
_cpu_name = None
if sys.platform == 'win32':
    try:
        import wmi
        _wmi = wmi.WMI()
        _cpu_name = _wmi.Win32_Processor()[0].Name.strip()
    except Exception:
        _cpu_name = platform.processor()
elif sys.platform.startswith('linux'):
    try:
        # Try /proc/cpuinfo first
        with open('/proc/cpuinfo') as f:
            for line in f:
                if 'model name' in line:
                    _cpu_name = line.split(':', 1)[1].strip()
                    break
    except Exception:
        pass
    if not _cpu_name:
        try:
            import subprocess
            _cpu_name = subprocess.check_output(['lscpu'], text=True)
            for line in _cpu_name.splitlines():
                if 'Model name' in line:
                    _cpu_name = line.split(':', 1)[1].strip()
                    break
        except Exception:
            _cpu_name = platform.processor()
else:
    _cpu_name = platform.processor()

class SystemInfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(18)
        # Section: System
        sys_header = QLabel('System')
        sys_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        sys_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        layout.addWidget(sys_header)
        sys_card = QFrame()
        sys_card.setStyleSheet('background: rgba(30,40,50,0.7); border-radius: 10px; padding: 12px;')
        sys_layout = QVBoxLayout()
        self.os_label = QLabel()
        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        sys_layout.addWidget(self.os_label)
        sys_layout.addWidget(self.cpu_label)
        sys_layout.addWidget(self.ram_label)
        sys_card.setLayout(sys_layout)
        layout.addWidget(sys_card)
        # Section: Live Usage
        usage_header = QLabel('Live Usage')
        usage_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        usage_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        layout.addWidget(usage_header)
        usage_card = QFrame()
        usage_card.setStyleSheet('background: rgba(20,30,40,0.8); border-radius: 10px; padding: 16px;')
        circ_row = QHBoxLayout()
        circ_row.setSpacing(32)
        circ_row.addStretch(1)
        # CPU
        self.cpu_circ = CircularProgress('CPU', QColor(0, 180, 255), self)
        self.cpu_circ.setToolTip('CPU Usage')
        self.cpu_circ.setFixedSize(140, 140)
        circ_row.addWidget(self.cpu_circ)
        # RAM
        self.ram_circ = CircularProgress('RAM', QColor(0, 255, 120), self)
        self.ram_circ.setToolTip('RAM Usage')
        self.ram_circ.setFixedSize(140, 140)
        circ_row.addWidget(self.ram_circ)
        # DISK(s)
        self.disk_circs = []
        disk_partitions = psutil.disk_partitions()
        if len(disk_partitions) > 1:
            disk_group = QVBoxLayout()
            # Removed disk_label
            from PyQt6.QtWidgets import QGridLayout
            disks_grid = QGridLayout()
            disks_grid.setHorizontalSpacing(12)
            disks_grid.setVerticalSpacing(12)
            for idx, part in enumerate(disk_partitions):
                circ = CircularProgress(part.device.rstrip('\\/'), QColor(255, 180, 0), self)
                circ.setToolTip(f"Disk {part.device}")
                circ.setFixedSize(70, 70)
                circ.thickness = 7  # Custom attribute for thin ring
                circ.font_size = 9  # Custom attribute for small text
                self.disk_circs.append(circ)
                row = idx % 2  # max 2 rows
                col = idx // 2
                disks_grid.addWidget(circ, row, col)
            disk_group.addLayout(disks_grid)
            circ_row.addLayout(disk_group)
        else:
            self.disk_circ = CircularProgress('DISK', QColor(255, 180, 0), self)
            self.disk_circ.setToolTip('Disk Usage')
            self.disk_circ.setFixedSize(140, 140)
            circ_row.addWidget(self.disk_circ)
        circ_row.addStretch(1)
        usage_card.setLayout(circ_row)
        layout.addWidget(usage_card)
        # Section: Battery
        batt_header = QLabel('Battery')
        batt_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        batt_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        layout.addWidget(batt_header)
        batt_card = QFrame()
        batt_card.setStyleSheet('background: rgba(30,40,50,0.7); border-radius: 10px; padding: 12px;')
        batt_layout = QHBoxLayout()
        batt_layout.setSpacing(12)
        self.battery_label = QLabel()
        self.battery_label.setFont(QFont('Consolas', 14))
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setFixedHeight(18)
        self.battery_bar.setTextVisible(False)
        self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {border-radius: 8px;}')
        batt_layout.addWidget(self.battery_label)
        batt_layout.addWidget(self.battery_bar)
        batt_card.setLayout(batt_layout)
        layout.addWidget(batt_card)
        layout.addStretch(1)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        self.update_info()

    def update_info(self):
        self.os_label.setText(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
        self.cpu_label.setText(f"CPU: {os.cpu_count()} cores, {_cpu_name}")
        self.ram_label.setText(f"RAM: {round(psutil.virtual_memory().used/1024**3,2)} / {round(psutil.virtual_memory().total/1024**3,2)} GB")
        cpu_percent = psutil.cpu_percent()
        self.cpu_circ.setValue(cpu_percent)
        ram_percent = psutil.virtual_memory().percent
        self.ram_circ.setValue(ram_percent)
        disk_partitions = psutil.disk_partitions()
        if len(disk_partitions) > 1:
            for i, part in enumerate(disk_partitions):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    percent = usage.percent
                except Exception:
                    percent = 0
                if i < len(self.disk_circs):
                    self.disk_circs[i].setValue(percent)
        else:
            disk = psutil.disk_usage('/')
            self.disk_circ.setValue(disk.percent)
        if hasattr(psutil, 'sensors_battery'):
            batt = psutil.sensors_battery()
            if batt:
                self.battery_label.setText(f"{batt.percent}% {'(Charging)' if batt.power_plugged else ''}")
                self.battery_bar.setValue(int(batt.percent))
                # Color battery bar
                if batt.percent > 60:
                    self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {background: #00ff88; border-radius: 8px;}')
                elif batt.percent > 20:
                    self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {background: #ffe066; border-radius: 8px;}')
                else:
                    self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {background: #ff4444; border-radius: 8px;}')
            else:
                self.battery_label.setText("N/A")
                self.battery_bar.setValue(0)
        else:
            self.battery_label.setText("N/A")
            self.battery_bar.setValue(0)
