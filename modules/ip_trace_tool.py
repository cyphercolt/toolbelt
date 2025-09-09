from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
import requests

class IPTraceWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
    def run(self):
        try:
            url = f"http://ip-api.com/json/{self.ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,asname,query"
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if data.get('status') == 'success':
                lines = [
                    f"IP: {data.get('query','')}\nCountry: {data.get('country','')}\nRegion: {data.get('regionName','')}\nCity: {data.get('city','')}\nZIP: {data.get('zip','')}\nLatitude: {data.get('lat','')}\nLongitude: {data.get('lon','')}\nISP: {data.get('isp','')}\nOrg: {data.get('org','')}\nASN: {data.get('asname','')}"
                ]
                result = '\n'.join(lines)
            else:
                result = f"Error: {data.get('message','Unknown error')}"
        except Exception as e:
            result = f"Error: {e}"
        self.result.emit(result)

class IPTraceTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        # Input row
        row = QHBoxLayout()
        row.addWidget(QLabel('IP or Domain:'))
        self.input = QLineEdit()
        self.input.setPlaceholderText('e.g. 8.8.8.8 or example.com')
        row.addWidget(self.input)
        self.trace_btn = QPushButton('Trace')
        self.trace_btn.clicked.connect(self.start_trace)
        row.addWidget(self.trace_btn)
        layout.addLayout(row)
        # Result box
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)
        # Effects button row (bottom left)
        self.effect_crt = False
        self.effect_scanline = False
        self.effect_glitch = False
        self.effect_shake = False
        self._scanline_overlay = None
        self._glitch_timer = None
        self._shake_flash_timer = None
        bottom_row = QHBoxLayout()
        self.effects_btn = QPushButton('Effects')
        self.effects_btn.setFixedWidth(90)
        self.effects_btn.clicked.connect(self.open_effects_menu)
        bottom_row.addWidget(self.effects_btn)
        bottom_row.addStretch(1)
        layout.addLayout(bottom_row)
        # IP info and maps row
        ipinfo_row = QHBoxLayout()
        self.local_ip_label = QLabel('Local IP: ...')
        self.wan_ip_label = QLabel('WAN IP: ...')
        ipinfo_row.addWidget(self.local_ip_label)
        ipinfo_row.addSpacing(20)
        ipinfo_row.addWidget(self.wan_ip_label)
        ipinfo_row.addStretch(1)
        self.maps_btn = QPushButton('Maps')
        self.maps_btn.setVisible(False)
        self.maps_btn.clicked.connect(self.open_maps_url)
        ipinfo_row.addWidget(self.maps_btn)
        layout.addLayout(ipinfo_row)
        self.setLayout(layout)
        self.worker = None
        self.update_ip_labels()
        self.update_result_effects()

    def open_effects_menu(self):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        from PyQt6.QtCore import QTimer
        menu = QMenu(self)
        crt_action = QAction('CRT', self, checkable=True)
        scanline_action = QAction('Scanline', self, checkable=True)
        glitch_action = QAction('Glitch', self, checkable=True)
        shake_action = QAction('Shake', self, checkable=True)
        crt_action.setChecked(self.effect_crt)
        scanline_action.setChecked(self.effect_scanline)
        glitch_action.setChecked(self.effect_glitch)
        shake_action.setChecked(self.effect_shake)
        def toggle_crt():
            self.effect_crt = not self.effect_crt
            self.update_result_effects()
        def toggle_scanline():
            self.effect_scanline = not self.effect_scanline
            self.update_result_effects()
        def toggle_glitch():
            self.effect_glitch = not self.effect_glitch
            self.update_result_effects()
        def toggle_shake():
            self.effect_shake = not self.effect_shake
            if self.effect_shake:
                if not self._shake_flash_timer:
                    self._shake_flash_timer = QTimer(self)
                    self._shake_flash_timer.timeout.connect(self._do_shake_flash)
                self._set_next_shake_flash_interval()
            else:
                if self._shake_flash_timer:
                    self._shake_flash_timer.stop()
                    self._shake_flash_timer = None
            self.update_result_effects()
        crt_action.triggered.connect(toggle_crt)
        scanline_action.triggered.connect(toggle_scanline)
        glitch_action.triggered.connect(toggle_glitch)
        shake_action.triggered.connect(toggle_shake)
        menu.addAction(crt_action)
        menu.addAction(scanline_action)
        menu.addAction(glitch_action)
        menu.addAction(shake_action)
        menu.exec(self.effects_btn.mapToGlobal(self.effects_btn.rect().bottomLeft()))
    def _set_next_shake_flash_interval(self):
        from PyQt6.QtCore import QTimer
        import random
        if self._shake_flash_timer:
            interval = random.randint(4000, 15000)
            self._shake_flash_timer.start(interval)

    def _do_shake_flash(self):
        # Apply invisible border (same as background) to shift text, then remove
        orig_style = self.result_box.styleSheet()
        if 'border: 2px solid #101014;' not in orig_style:
            self.result_box.setStyleSheet(orig_style + 'border: 2px solid #101014;')
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(150, lambda: self._remove_invisible_shake_border(orig_style))
        self._set_next_shake_flash_interval()

    def _remove_invisible_shake_border(self, orig_style):
        # Remove the invisible border
        self.result_box.setStyleSheet(orig_style.replace('border: 2px solid #101014;', ''))

    def update_result_effects(self):
        # CRT effect: green text, bold font
        if self.effect_crt:
            self.result_box.setStyleSheet('background: #101014; color: #39ff14; font-family: Consolas; font-size: 14px; font-weight: bold;')
        else:
            self.result_box.setStyleSheet('background: #101014; color: #c0c0ff; font-family: Consolas; font-size: 14px;')
        # Shake effect: red border flash (timer managed in toggle)
        if not getattr(self, 'effect_shake', False):
            if hasattr(self, '_shake_flash_timer') and self._shake_flash_timer:
                self._shake_flash_timer.stop()
                self._shake_flash_timer = None
        # Scanline effect: overlay widget with lines
        from modules.scanline_overlay import ScanlineOverlay
        if self.effect_scanline:
            if not self._scanline_overlay:
                self._scanline_overlay = ScanlineOverlay(self.result_box)
                self._scanline_overlay.setParent(self.result_box.viewport())
                self._scanline_overlay.raise_()
            self._scanline_overlay.resize(self.result_box.viewport().size())
            self._scanline_overlay.show()
        else:
            if self._scanline_overlay:
                self._scanline_overlay.hide()
        # Glitch effect: animated character glitch
        from PyQt6.QtCore import QTimer
        import random
        if self.effect_glitch:
            if not self._glitch_timer:
                self._glitch_timer = QTimer(self)
                self._glitch_timer.timeout.connect(self._do_glitch)
            self._set_next_glitch_interval()
        else:
            if self._glitch_timer:
                self._glitch_timer.stop()
                self._glitch_timer = None
            if hasattr(self, '_glitching') and self._glitching:
                self._restore_result_text()

    def _set_next_glitch_interval(self):
        import random
        if self._glitch_timer:
            interval = random.randint(3000, 15000)
            self._glitch_timer.start(interval)
            self._glitching = False

    def _do_glitch(self):
        import random
        if not hasattr(self, '_original_text'):
            self._original_text = self.result_box.toPlainText()
        text = self.result_box.toPlainText()
        if not text.strip():
            return
        self._original_text = text
        # Save current scroll position
        scroll_bar = self.result_box.verticalScrollBar()
        scroll_pos = scroll_bar.value()
        lines = text.splitlines()
        glitch_chars = '█▓▒░@#$%&*?!/\\|><~'
        X = 30
        start_idx = max(0, len(lines) - X)
        for _ in range(random.randint(2, 6)):
            if len(lines) == 0:
                break
            line_idx = random.randint(start_idx, len(lines)-1)
            if not lines[line_idx]:
                continue
            char_idx = random.randint(0, len(lines[line_idx])-1)
            gl = random.choice(glitch_chars)
            lines[line_idx] = lines[line_idx][:char_idx] + gl + lines[line_idx][char_idx+1:]
        self.result_box.setPlainText('\n'.join(lines))
        scroll_bar.setValue(scroll_pos)
        self._glitching = True
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(120, lambda: self._restore_result_text(scroll_pos))
        self._set_next_glitch_interval()

    def _restore_result_text(self, scroll_pos=None):
        if hasattr(self, '_original_text'):
            self.result_box.setPlainText(self._original_text)
            if scroll_pos is not None:
                self.result_box.verticalScrollBar().setValue(scroll_pos)
        self._glitching = False

    def update_ip_labels(self):
        # Local IP
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = 'N/A'
        self.local_ip_label.setText(f'Local IP: {local_ip}')
        # WAN IP
        try:
            import requests
            wan_ip = requests.get('https://api.ipify.org', timeout=5).text
        except Exception:
            wan_ip = 'N/A'
        self.wan_ip_label.setText(f'WAN IP: {wan_ip}')
    def start_trace(self):
        ip = self.input.text().strip()
        if not ip:
            self.result_box.setText('Please enter an IP or domain.')
            return
        self.result_box.setText('Tracing...')
        self.trace_btn.setEnabled(False)
        self.worker = IPTraceWorker(ip)
        self.worker.result.connect(self.on_result)
        self.worker.start()
    def on_result(self, text):
        self.result_box.setText(text)
        self.trace_btn.setEnabled(True)
        # Parse latitude and longitude from the output
        import re
        lat_match = re.search(r'^Latitude: ([\-0-9.]+)', text, re.MULTILINE)
        lon_match = re.search(r'^Longitude: ([\-0-9.]+)', text, re.MULTILINE)
        if lat_match and lon_match:
            lat = lat_match.group(1)
            lon = lon_match.group(1)
            self.maps_url = f'https://maps.google.com/?q={lat},{lon}'
            self.maps_btn.setVisible(True)
        else:
            self.maps_url = None
            self.maps_btn.setVisible(False)

    def open_maps_url(self):
        import webbrowser
        if hasattr(self, 'maps_url') and self.maps_url:
            webbrowser.open(self.maps_url)
