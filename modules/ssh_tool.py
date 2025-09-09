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
            import time
            while self.running and self.channel and not self.channel.closed:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096).decode(errors='ignore')
                    self.output.emit(data)
                time.sleep(0.01)
        except (paramiko.ssh_exception.SSHException, socket.error) as e:
            self.output.emit(f"Connection error: {e}\n")
            self.connected.emit(False)
        finally:
            if self.client:
                self.client.close()

class SSHTool(QWidget):
    def closeEvent(self, event):
        # Gracefully stop the SSH worker thread if running
        if hasattr(self, 'worker') and self.worker is not None:
            try:
                self.worker.stop()
                self.worker.wait(1000)  # Wait up to 1s for thread to finish
            except Exception:
                pass
        event.accept()
    def open_effects_menu(self):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        menu = QMenu(self)
        crt_action = QAction('CRT', self)
        crt_action.setCheckable(True)
        crt_action.setChecked(self.effect_crt)
        scanline_action = QAction('Scanline', self)
        scanline_action.setCheckable(True)
        scanline_action.setChecked(self.effect_scanline)
        glitch_action = QAction('Glitch', self)
        glitch_action.setCheckable(True)
        glitch_action.setChecked(self.effect_glitch)
        shake_action = QAction('Shake', self)
        shake_action.setCheckable(True)
        shake_action.setChecked(self.effect_shake)
        def toggle_crt():
            self.effect_crt = not self.effect_crt
            self.update_terminal_effects()
        def toggle_scanline():
            self.effect_scanline = not self.effect_scanline
            self.update_terminal_effects()
        def toggle_glitch():
            self.effect_glitch = not self.effect_glitch
            self.update_terminal_effects()
        def toggle_shake():
            self.effect_shake = not self.effect_shake
            self.update_terminal_effects()
        crt_action.triggered.connect(toggle_crt)
        scanline_action.triggered.connect(toggle_scanline)
        glitch_action.triggered.connect(toggle_glitch)
        shake_action.triggered.connect(toggle_shake)
        menu.addAction(crt_action)
        menu.addAction(scanline_action)
        menu.addAction(glitch_action)
        menu.addAction(shake_action)
        menu.exec(self.effects_btn.mapToGlobal(self.effects_btn.rect().bottomLeft()))
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
        # Initialize effect overlay/timer attributes
        self._scanline_overlay = None
        self._crt_overlay = None
        self._glitch_timer = None
        self._shake_timer = None
        # Initialize effect state variables before any usage
        self.effect_crt = False
        self.effect_scanline = False
        self.effect_glitch = False
        self.effect_shake = False
        super().__init__(parent)
        from PyQt6.QtCore import QTimer
        layout = QVBoxLayout()
    # Remove SSH Connect button from top, will be placed under input
        self.os_label = QLabel("Not connected")
        layout.addWidget(self.os_label)
        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("SSH Output...")
        layout.addWidget(self.terminal)

        # Effects button row (bottom left)
        bottom_row = QHBoxLayout()
        self.effects_btn = QPushButton('Effects')
        self.effects_btn.clicked.connect(self.open_effects_menu)
        bottom_row.addWidget(self.effects_btn)
        bottom_row.addStretch(1)
        layout.addLayout(bottom_row)

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
        from PyQt6.QtCore import QTimer
        self._output_buffer = []
        self._output_timer = QTimer(self)
        self._output_timer.setInterval(50)  # ms, adjust as needed
        self._output_timer.timeout.connect(self._flush_terminal_output)
        # Effects state
        self.effect_crt = False
        self.effect_scanline = False
        self.effect_glitch = False
        # Effects and SSH Connect button row (under input)
        button_row = QHBoxLayout()
        self.effects_btn = QPushButton('Effects')
        self.effects_btn.setFixedWidth(90)
        self.effects_btn.clicked.connect(self.open_effects_menu)
        button_row.addWidget(self.effects_btn)
        self.ssh_btn = QPushButton("SSH Connect")
        self.ssh_btn.setFixedWidth(110)
        self.ssh_btn.clicked.connect(self.open_ssh_dialog)
        button_row.addWidget(self.ssh_btn)
        button_row.addStretch(1)
        layout.addLayout(button_row)

    def update_terminal_effects(self):
        # CRT effect: green text, bold font
        if getattr(self, 'effect_crt', False):
            self.terminal.setStyleSheet('background: #101014; color: #39ff14; font-family: Consolas; font-size: 14px; font-weight: bold;')
        else:
            self.terminal.setStyleSheet('background: #101014; color: #c0c0ff; font-family: Consolas; font-size: 14px;')
        # Scanline effect: overlay widget with lines
        from modules.scanline_overlay import ScanlineOverlay
        if getattr(self, 'effect_scanline', False):
            if not self._scanline_overlay:
                self._scanline_overlay = ScanlineOverlay(self.terminal)
                self._scanline_overlay.setParent(self.terminal.viewport())
                self._scanline_overlay.raise_()
            self._scanline_overlay.resize(self.terminal.viewport().size())
            self._scanline_overlay.show()
        else:
            if self._scanline_overlay:
                self._scanline_overlay.hide()
        # Glitch effect
        from PyQt6.QtCore import QTimer
        import random
        if getattr(self, 'effect_glitch', False):
            if not self._glitch_timer:
                self._glitch_timer = QTimer(self)
                self._glitch_timer.timeout.connect(self._do_glitch)
            self._set_next_glitch_interval()
        else:
            if self._glitch_timer:
                self._glitch_timer.stop()
                self._glitch_timer = None
            if hasattr(self, '_glitching') and self._glitching:
                self._restore_terminal_text()

    def _set_next_glitch_interval(self):
        import random
        if self._glitch_timer:
            interval = random.randint(3000, 15000)
            self._glitch_timer.start(interval)
            self._glitching = False

    def _do_glitch(self):
        import random
        text = self.terminal.toPlainText()
        if not text.strip():
            return
        self._original_text = text
        scroll_bar = self.terminal.verticalScrollBar()
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
        self.terminal.setPlainText('\n'.join(lines))
        scroll_bar.setValue(scroll_pos)
        self._glitching = True
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(120, lambda: self._restore_terminal_text(scroll_pos))
        self._set_next_glitch_interval()

    def _restore_terminal_text(self, scroll_pos=None):
        if hasattr(self, '_original_text'):
            self.terminal.setPlainText(self._original_text)
            if scroll_pos is not None:
                self.terminal.verticalScrollBar().setValue(scroll_pos)
        self._glitching = False

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


