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
        row = QHBoxLayout()
        row.addWidget(QLabel('IP or Domain:'))
        self.input = QLineEdit()
        self.input.setPlaceholderText('e.g. 8.8.8.8 or example.com')
        row.addWidget(self.input)
        self.trace_btn = QPushButton('Trace')
        self.trace_btn.clicked.connect(self.start_trace)
        row.addWidget(self.trace_btn)
        layout.addLayout(row)
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)
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
