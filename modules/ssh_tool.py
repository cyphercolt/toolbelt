from PyQt6.QtWidgets import QLineEdit

class InputLine(QLineEdit):
    def __init__(self, parent=None, history_ref=None, index_ref=None):
        super().__init__(parent)
        self._history_ref = history_ref
        self._index_ref = index_ref

    def keyPressEvent(self, event):
        from PyQt6.QtCore import Qt
        key = event.key()
        history = self._history_ref() if self._history_ref else []
        index = self._index_ref() if self._index_ref else 0
        if key == Qt.Key.Key_Up:
            if history and index > 0:
                index -= 1
                self.setText(history[index])
                if self._index_ref:
                    self._index_ref(index)
            return
        elif key == Qt.Key.Key_Down:
            if history and index < len(history) - 1:
                index += 1
                self.setText(history[index])
            else:
                index = len(history)
                self.clear()
            if self._index_ref:
                self._index_ref(index)
            return
        super().keyPressEvent(event)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QLabel, QHBoxLayout, QTextEdit)
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import paramiko
import socket
import re

class SSHWorker(QThread):
    def stop(self):
        self.running = False
        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
    output = pyqtSignal(str)
    os_detected = pyqtSignal(str)
    connected = pyqtSignal(bool)
    command_input = pyqtSignal(str)


    def send_command(self, cmd):
        if self.channel and self.channel.send_ready():
            self.channel.send(cmd + '\n')

    def __init__(self, hostname, username, password):
        super().__init__()
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client = None
        self.channel = None
        self.running = True
        self.command_input.connect(self.send_command)

    def run(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, username=self.username, password=self.password, timeout=8)
            self.channel = self.client.invoke_shell()
            self.connected.emit(True)
            # Detect OS
            stdin, stdout, stderr = self.client.exec_command('uname -a')
            os_info = stdout.read().decode().strip()
            if os_info:
                self.os_detected.emit('Linux')
            else:
                stdin, stdout, stderr = self.client.exec_command('ver')
                os_info = stdout.read().decode().strip()
                if 'Windows' in os_info:
                    self.os_detected.emit('Windows')
                else:
                    self.os_detected.emit('Unknown')
            while self.running and self.channel and not self.channel.closed:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096).decode(errors='ignore')
                    self.output.emit(data)
        except (paramiko.ssh_exception.SSHException, socket.error) as e:
            self.output.emit(f"Connection error: {e}\n")
            self.connected.emit(False)
        finally:
            if self.client:
                self.client.close()

class SSHTool(QWidget):
    def set_connected(self, ok):
        self.connected = ok
        self.input_line.setEnabled(ok)
        if not ok:
            self.os_label.setText("Connection failed")
    def set_os_label(self, os_name):
        self.os_label.setText(f"Connected: {os_name}")
    def append_terminal(self, text):
        # If skipping output after clear, ignore all output for a short period
        if getattr(self, '_skip_output_until', False):
            return
        # Buffer output and flush with timer to avoid UI lag
        self._output_buffer.append(text)
        if not self._output_timer.isActive():
            self._output_timer.start()
    def _flush_terminal_output(self):
        import re
        if not self._output_buffer:
            self._output_timer.stop()
            return
        batch = ''.join(self._output_buffer)
        self._output_buffer.clear()
        ansi_escape = re.compile(r'\x1B\[[0-9;?]*[A-Za-z]|\x1B\][0-9];.*?\x07|\x1B\(B|\x1B\)0|\x1B\[\?2004[hl]|\x07|\r')
        clean_text = ansi_escape.sub('', batch)
        if clean_text.strip() == '' and 'clear' in batch:
            self.terminal.clear()
        elif 'clear' in clean_text and clean_text.strip() == 'clear':
            self.terminal.clear()
        elif clean_text:
            self.terminal.insertPlainText(clean_text)
            self.terminal.moveCursor(QTextCursor.MoveOperation.End)
        self._output_timer.stop()
    def on_send_command(self):
        if not self.connected or not self.worker or not hasattr(self.worker, 'channel') or not self.worker.channel or self.worker.channel.closed:
            return
        cmd = self.input_line.text().strip()
        if cmd == "clear":
            self.terminal.clear()
            self._output_buffer.clear()
            self._skip_output_until = True
            from PyQt6.QtCore import QTimer
            if not hasattr(self, '_clear_timer'):
                self._clear_timer = QTimer(self)
                self._clear_timer.setSingleShot(True)
                self._clear_timer.timeout.connect(self._end_skip_output)
            self._clear_timer.start(100)  # ms
        if cmd and self.worker and hasattr(self.worker, 'command_input'):
            self.worker.command_input.emit(cmd)
            # Add to history, avoid duplicates in a row
            if not self.command_history or (self.command_history and self.command_history[-1] != cmd):
                self.command_history.append(cmd)
            self.history_index = len(self.command_history)
            self.input_line.clear()

    def _end_skip_output(self):
        self._skip_output_until = False
    def keyPressEvent(self, event):
        # Only handle up/down arrows in the input_line
        if self.input_line.hasFocus():
            key = event.key()
            from PyQt6.QtCore import Qt
            if key == Qt.Key.Key_Up:
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.command_history[self.history_index])
                return
            elif key == Qt.Key.Key_Down:
                if self.command_history and self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input_line.setText(self.command_history[self.history_index])
                else:
                    self.history_index = len(self.command_history)
                    self.input_line.clear()
                return
        super().keyPressEvent(event)

    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt6.QtCore import QTimer
        layout = QVBoxLayout()
        self.ssh_btn = QPushButton("SSH Connect")
        self.ssh_btn.clicked.connect(self.open_ssh_dialog)
        layout.addWidget(self.ssh_btn)
        self.os_label = QLabel("Not connected")
        layout.addWidget(self.os_label)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("SSH Output...")
        layout.addWidget(self.terminal)
        # Use custom InputLine for command history navigation
        def get_history():
            return self.command_history
        def get_index(val=None):
            if val is not None:
                self.history_index = val
            return self.history_index
        self.input_line = InputLine(history_ref=get_history, index_ref=get_index)
        self.input_line.setPlaceholderText("Type command and press Enter...")
        self.input_line.returnPressed.connect(self.on_send_command)
        layout.addWidget(self.input_line)
        self.worker = None
        self.connected = False
        self.command_history = []
        self.history_index = 0
        self.setLayout(layout)
        self.setMinimumSize(700, 400)
        # Terminal output buffer and timer for batching
        self._output_buffer = []
        self._output_timer = QTimer(self)
        self._output_timer.setInterval(50)  # ms, adjust as needed
        self._output_timer.timeout.connect(self._flush_terminal_output)

    def open_ssh_dialog(self):
        dlg = SSHDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            host, user, passwd = dlg.get_data()
            self.start_ssh(host, user, passwd)

    def start_ssh(self, host, user, passwd):
        if self.worker:
            self.worker.stop()
        self.terminal.clear()
        self.worker = SSHWorker(host, user, passwd)
        self.worker.output.connect(self.append_terminal)
        self.worker.os_detected.connect(self.set_os_label)
        self.worker.connected.connect(self.set_connected)
        self.worker.start()

class SSHDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Connect")
        self.setModal(True)
        layout = QVBoxLayout()
        self.host_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Host/IP:"))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.pass_input)
        btns = QHBoxLayout()
        self.ok_btn = QPushButton("Connect")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return self.host_input.text(), self.user_input.text(), self.pass_input.text()


