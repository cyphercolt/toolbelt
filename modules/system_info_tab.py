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
        # Usage Card Row (CPU, RAM, GPU, Disks)
        usage_card = QFrame()
        usage_card.setStyleSheet('background: rgba(30,40,50,0.7); border-radius: 10px; padding: 12px;')
        circ_row = QHBoxLayout()
        circ_row.setSpacing(18)
        circ_row.setContentsMargins(0, 0, 0, 0)
        # CPU
        self.cpu_circ = CircularProgress('CPU', QColor(0, 200, 255), self)
        self.cpu_circ.setToolTip('CPU Usage')
        self.cpu_circ.setFixedSize(140, 140)
        circ_row.addWidget(self.cpu_circ)
        # RAM
        self.ram_circ = CircularProgress('RAM', QColor(0, 255, 140), self)
        self.ram_circ.setToolTip('RAM Usage')
        self.ram_circ.setFixedSize(140, 140)
        circ_row.addWidget(self.ram_circ)
        # GPU
        self.gpu_circ = CircularProgress('GPU', QColor(255, 100, 100), self)
        self.gpu_circ.setToolTip('GPU Usage')
        self.gpu_circ.setFixedSize(140, 140)
        circ_row.addWidget(self.gpu_circ)
        # DISK(s)
        self.disk_circs = []
        disk_partitions = psutil.disk_partitions()
        if len(disk_partitions) > 1:
            disk_group = QVBoxLayout()
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
        # Section: System
        sys_header = QLabel('System')
        sys_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        sys_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        layout.addWidget(sys_header)
        from PyQt6.QtWidgets import QGridLayout
        sys_grid = QGridLayout()
        sys_grid.setHorizontalSpacing(18)
        sys_grid.setVerticalSpacing(4)
        # Labels
        os_title = QLabel('OS:')
        cpu_title = QLabel('CPU:')
        ram_title = QLabel('RAM:')
        gpu_title = QLabel('GPU:')
        drives_title = QLabel('Drives:')
        for t in (os_title, cpu_title, ram_title, gpu_title, drives_title):
            t.setFont(QFont('Consolas', 10, QFont.Weight.Bold))
            t.setStyleSheet('color: #7ecfff;')
        self.os_label = QLabel()
        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        self.gpu_label = QLabel()
        for l in (self.os_label, self.cpu_label, self.ram_label, self.gpu_label):
            l.setFont(QFont('Consolas', 10))
            l.setStyleSheet('color: #b0eaff;')
        sys_grid.addWidget(os_title, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        sys_grid.addWidget(self.os_label, 0, 1)
        sys_grid.addWidget(cpu_title, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        sys_grid.addWidget(self.cpu_label, 1, 1)
        sys_grid.addWidget(ram_title, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        sys_grid.addWidget(self.ram_label, 2, 1)
        sys_grid.addWidget(gpu_title, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        sys_grid.addWidget(self.gpu_label, 3, 1)
        sys_grid.addWidget(drives_title, 4, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        # Drives area (no box, dynamic)
        self.sys_drive_layout = QVBoxLayout()
        self.sys_drive_layout.setSpacing(1)
        self.sys_drive_layout.setContentsMargins(0, 0, 0, 0)
        self.sys_drive_labels = []
        sys_grid.addLayout(self.sys_drive_layout, 4, 1, alignment=Qt.AlignmentFlag.AlignTop)
        sys_grid.setColumnStretch(1, 1)
        layout.addLayout(sys_grid)

        # Battery widgets (created here, added dynamically in update_info)
        self.batt_header = QLabel('Battery')
        self.batt_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        self.batt_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        self.batt_card = QFrame()
        self.batt_card.setStyleSheet('background: rgba(30,40,50,0.7); border-radius: 10px; padding: 12px;')
        self.batt_layout = QHBoxLayout()
        self.batt_layout.setSpacing(12)
        self.battery_label = QLabel()
        self.battery_label.setFont(QFont('Consolas', 14))
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setFixedHeight(18)
        self.battery_bar.setTextVisible(False)
        self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {border-radius: 8px;}')
        self.batt_layout.addWidget(self.battery_label)
        self.batt_layout.addWidget(self.battery_bar)
        self.batt_card.setLayout(self.batt_layout)
        # Add battery widgets later in update_info if present

        layout.addStretch(1)
        self.setLayout(layout)
        self._main_layout = layout  # Save for dynamic widget add/remove
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        self.update_info()
        self.os_label.setText(f"{platform.system()} {platform.release()} ({platform.machine()})")
        self.cpu_label.setText(f"{os.cpu_count()} cores, {_cpu_name}")
        self.ram_label.setText(f"{round(psutil.virtual_memory().used/1024**3,2)} / {round(psutil.virtual_memory().total/1024**3,2)} GB")
        self.gpu_label.setText(f"{self.get_gpu_name()}")
        # Drives info (right side)
        for lbl in self.sys_drive_labels:
            self.sys_drive_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.sys_drive_labels.clear()
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = usage.total / 1024**3
                used_gb = usage.used / 1024**3
                label = QLabel(f"{part.device}  {used_gb:.1f}/{total_gb:.1f} GB")
                label.setFont(QFont('Consolas', 8))
                label.setStyleSheet('color: #a0c8e0; padding: 0; margin: 0;')
                label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.sys_drive_layout.addWidget(label)
                self.sys_drive_labels.append(label)
            except Exception:
                continue
        cpu_percent = psutil.cpu_percent()
        self.cpu_circ.setValue(cpu_percent)
        ram_percent = psutil.virtual_memory().percent
        self.ram_circ.setValue(ram_percent)
        gpu_percent = self.get_gpu_usage()
        if gpu_percent is not None:
            self.gpu_circ.setValue(gpu_percent)
            self.gpu_circ.show()
        else:
            self.gpu_circ.hide()
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
        # Dynamically show/hide battery section
        if hasattr(psutil, 'sensors_battery'):
            batt = psutil.sensors_battery()
            if batt:
                if self._main_layout.indexOf(self.batt_header) == -1:
                    self._main_layout.addWidget(self.batt_header)
                if self._main_layout.indexOf(self.batt_card) == -1:
                    self._main_layout.addWidget(self.batt_card)
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
                if self._main_layout.indexOf(self.batt_header) != -1:
                    self._main_layout.removeWidget(self.batt_header)
                    self.batt_header.setParent(None)
                if self._main_layout.indexOf(self.batt_card) != -1:
                    self._main_layout.removeWidget(self.batt_card)
                    self.batt_card.setParent(None)
        else:
            if self._main_layout.indexOf(self.batt_header) != -1:
                self._main_layout.removeWidget(self.batt_header)
                self.batt_header.setParent(None)
            if self._main_layout.indexOf(self.batt_card) != -1:
                self._main_layout.removeWidget(self.batt_card)
                self.batt_card.setParent(None)
                # Removed invalid leftover disk widget code
        # Section: Battery (conditionally shown)
        self.batt_header = QLabel('Battery')
        self.batt_header.setFont(QFont('Consolas', 18, QFont.Weight.Bold))
        self.batt_header.setStyleSheet('color: #7ecfff; padding-bottom: 4px;')
        self.batt_card = QFrame()
        self.batt_card.setStyleSheet('background: rgba(30,40,50,0.7); border-radius: 10px; padding: 12px;')
        self.batt_layout = QHBoxLayout()
        self.batt_layout.setSpacing(12)
        self.battery_label = QLabel()
        self.battery_label.setFont(QFont('Consolas', 14))
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setFixedHeight(18)
        self.battery_bar.setTextVisible(False)
        self.battery_bar.setStyleSheet('QProgressBar {background: #222; border-radius: 8px;} QProgressBar::chunk {border-radius: 8px;}')
        self.batt_layout.addWidget(self.battery_label)
        self.batt_layout.addWidget(self.battery_bar)
        self.batt_card.setLayout(self.batt_layout)
        # Add battery widgets later in update_info if present
        layout.addStretch(1)
        self.setLayout(layout)
        self._main_layout = layout  # Save for dynamic widget add/remove
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        self.update_info()

    def get_gpu_usage(self):
        import sys
        if sys.platform.startswith('linux') or sys.platform == 'win32':
            try:
                import subprocess
                result = subprocess.run([
                    'nvidia-smi',
                    '--query-gpu=utilization.gpu',
                    '--format=csv,noheader,nounits'
                ], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    usage = result.stdout.strip().split('\n')[0]
                    return float(usage)
            except Exception:
                pass
        return None
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

    def get_gpu_name(self):
        import sys
        # Windows: use wmi, fallback to nvidia-smi if virtual/basic
        if sys.platform == 'win32':
            gpu_name = None
            try:
                import wmi
                w = wmi.WMI()
                gpus = w.Win32_VideoController()
                if gpus:
                    gpu_name = gpus[0].Name
            except Exception:
                pass
            # Fallback if virtual/basic
            if gpu_name and any(x in gpu_name.lower() for x in ['virtual', 'basic', 'microsoft']):
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip().split('\n')[0]
                except Exception:
                    pass
            if gpu_name:
                return gpu_name
        # Linux: try nvidia-smi, then lspci
        elif sys.platform.startswith('linux'):
            try:
                import subprocess
                # Try nvidia-smi first
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except Exception:
                pass
            try:
                import subprocess
                result = subprocess.run(['lspci'], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if 'VGA compatible controller' in line or '3D controller' in line:
                        return line.split(':', 2)[-1].strip()
            except Exception:
                pass
        return 'N/A'

    def update_info(self):
        self.os_label.setText(f"{platform.system()} {platform.release()} ({platform.machine()})")
        self.cpu_label.setText(f"{os.cpu_count()} cores, {_cpu_name}")
        self.ram_label.setText(f"{round(psutil.virtual_memory().used/1024**3,2)} / {round(psutil.virtual_memory().total/1024**3,2)} GB")
        self.gpu_label.setText(f"{self.get_gpu_name()}")
        # Drives info (right side)
        for lbl in self.sys_drive_labels:
            self.sys_drive_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.sys_drive_labels.clear()
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = usage.total / 1024**3
                used_gb = usage.used / 1024**3
                label = QLabel(f"{part.device}  {used_gb:.1f}/{total_gb:.1f} GB")
                label.setFont(QFont('Consolas', 8))
                label.setStyleSheet('color: #a0c8e0; padding: 0; margin: 0;')
                label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.sys_drive_layout.addWidget(label)
                self.sys_drive_labels.append(label)
            except Exception:
                continue
        cpu_percent = psutil.cpu_percent()
        self.cpu_circ.setValue(cpu_percent)
        ram_percent = psutil.virtual_memory().percent
        self.ram_circ.setValue(ram_percent)
        gpu_percent = self.get_gpu_usage()
        if gpu_percent is not None:
            self.gpu_circ.setValue(gpu_percent)
            self.gpu_circ.show()
        else:
            self.gpu_circ.hide()
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
        # Dynamically show/hide battery section
        if hasattr(psutil, 'sensors_battery'):
            batt = psutil.sensors_battery()
            if batt:
                if self._main_layout.indexOf(self.batt_header) == -1:
                    self._main_layout.addWidget(self.batt_header)
                if self._main_layout.indexOf(self.batt_card) == -1:
                    self._main_layout.addWidget(self.batt_card)
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
                if self._main_layout.indexOf(self.batt_header) != -1:
                    self._main_layout.removeWidget(self.batt_header)
                    self.batt_header.setParent(None)
                if self._main_layout.indexOf(self.batt_card) != -1:
                    self._main_layout.removeWidget(self.batt_card)
                    self.batt_card.setParent(None)
        else:
            if self._main_layout.indexOf(self.batt_header) != -1:
                self._main_layout.removeWidget(self.batt_header)
                self.batt_header.setParent(None)
            if self._main_layout.indexOf(self.batt_card) != -1:
                self._main_layout.removeWidget(self.batt_card)
                self.batt_card.setParent(None)
