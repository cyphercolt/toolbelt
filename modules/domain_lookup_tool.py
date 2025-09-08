from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import socket

class DNSLookupWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
    def run(self):
        try:
            ip = socket.gethostbyname(self.domain)
            result = f"A record: {ip}\n"
        except Exception as e:
            result = f"A record: Error - {e}\n"
        # Try to get CNAME, MX, TXT if possible (using socket only for A)
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            # CNAME
            try:
                cname = resolver.resolve(self.domain, 'CNAME')
                for r in cname:
                    result += f"CNAME: {r.target}\n"
            except Exception:
                result += "CNAME: -\n"
            # MX
            try:
                mx = resolver.resolve(self.domain, 'MX')
                for r in mx:
                    result += f"MX: {r.exchange} (priority {r.preference})\n"
            except Exception:
                result += "MX: -\n"
            # TXT
            try:
                txt = resolver.resolve(self.domain, 'TXT')
                for r in txt:
                    result += f"TXT: {b''.join(r.strings).decode(errors='ignore')}\n"
            except Exception:
                result += "TXT: -\n"
        except Exception:
            result += "(Install 'dnspython' for more records)\n"
        self.result.emit(result)

class WhoisLookupWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
    def run(self):
        try:
            import whois
            w = whois.whois(self.domain)
            lines = []
            for k in ["domain_name", "registrar", "creation_date", "expiration_date", "name_servers", "org", "country", "emails"]:
                v = w.get(k, None)
                if v:
                    lines.append(f"{k.replace('_',' ').title()}: {v}")
            result = "WHOIS Info:\n" + ("\n".join(lines) if lines else "No WHOIS data found.")
        except Exception as e:
            result = f"WHOIS lookup error: {e}"
        self.result.emit(result)

class DomainLookupTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel('Domain:'))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText('e.g. example.com')
        row.addWidget(self.domain_input)
        self.lookup_btn = QPushButton('Lookup')
        self.lookup_btn.clicked.connect(self.start_lookup)
        row.addWidget(self.lookup_btn)
        self.whois_btn = QPushButton('WHOIS Lookup')
        self.whois_btn.clicked.connect(self.start_whois)
        row.addWidget(self.whois_btn)
        layout.addLayout(row)
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)
        self.setLayout(layout)
        self.worker = None
        self.whois_worker = None
    def start_lookup(self):
        domain = self.domain_input.text().strip()
        if not domain:
            self.result_box.setText('Please enter a domain.')
            return
        self.result_box.setText('Looking up...')
        self.lookup_btn.setEnabled(False)
        self.worker = DNSLookupWorker(domain)
        self.worker.result.connect(self.on_result)
        self.worker.start()
    def on_result(self, text):
        self.result_box.setText(text)
        self.lookup_btn.setEnabled(True)

    def start_whois(self):
        domain = self.domain_input.text().strip()
        if not domain:
            self.result_box.setText('Please enter a domain.')
            return
        self.result_box.append('\nWHOIS: Looking up...')
        self.whois_btn.setEnabled(False)
        self.whois_worker = WhoisLookupWorker(domain)
        self.whois_worker.result.connect(self.on_whois_result)
        self.whois_worker.start()

    def on_whois_result(self, text):
        self.result_box.append(text)
        self.whois_btn.setEnabled(True)
