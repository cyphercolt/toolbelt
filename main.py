import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from shared.theme import apply_oled_theme


class ToolBeltMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Belt")
        self.resize(900, 600)
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        # Exit button row
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        exit_btn = QPushButton("Exit")
        exit_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        exit_btn.clicked.connect(QApplication.instance().quit)
        btn_row.addWidget(exit_btn)
        main_layout.addLayout(btn_row)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # Import and add tool tabs after QApplication is created
        from modules.ssh_tool import SSHTool
        from modules.port_scanner_tool import PortScannerTool
        from modules.domain_lookup_tool import DomainLookupTool
        from modules.ip_trace_tool import IPTraceTool
        from modules.matrix_rain_tab import FunToolsTab
        from modules.system_info_tab import SystemInfoTab
        from modules.terminal_emulator import TerminalEmulator
        self.system_info_tab = SystemInfoTab()
        self.tabs.addTab(self.system_info_tab, "System Info")
        self.ssh_tool = SSHTool()
        self.tabs.addTab(self.ssh_tool, "SSH")
        self.port_scanner_tool = PortScannerTool()
        self.tabs.addTab(self.port_scanner_tool, "Port Scanner")
        self.domain_lookup_tool = DomainLookupTool()
        self.tabs.addTab(self.domain_lookup_tool, "Domain Lookup")
        self.ip_trace_tool = IPTraceTool()
        self.tabs.addTab(self.ip_trace_tool, "IP Trace")
        self.terminal_emulator = TerminalEmulator()
        self.tabs.addTab(self.terminal_emulator, "Terminal")
        self.fun_tools_tab = FunToolsTab(main_window=self)
        self.tabs.addTab(self.fun_tools_tab, "Fun Tools")
        apply_oled_theme(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToolBeltMainWindow()
    window.show()
    sys.exit(app.exec())
