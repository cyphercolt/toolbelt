from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLineEdit, QLabel, QComboBox, QColorDialog, QFontDialog
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QColor, QFont

from PyQt6.QtCore import QTimer

import shutil
import platform
import subprocess
from modules.scanline_overlay import ScanlineOverlay

class TerminalEmulator(QWidget):
    def update_terminal_effects(self):
        # CRT effect: green text, bold font
        if getattr(self, 'effect_crt', False):
            self.terminal.setStyleSheet('background: #101014; color: #39ff14; font-family: Consolas; font-size: 14px; font-weight: bold;')
        else:
            self.terminal.setStyleSheet('background: #101014; color: #c0c0ff; font-family: Consolas; font-size: 14px;')

        # Shake effect: red border flash (timer managed in toggle)
        if not getattr(self, 'effect_shake', False):
            if hasattr(self, '_shake_flash_timer'):
                self._shake_flash_timer.stop()
                del self._shake_flash_timer
            # No red border to remove

    def _set_next_shake_flash_interval(self):
        import random
        if hasattr(self, '_shake_flash_timer'):
            interval = random.randint(4000, 15000)  # 4 to 15 seconds
            self._shake_flash_timer.start(interval)

    def _do_shake_flash(self):
        # Apply invisible border to shift text
        self._apply_invisible_shake_border()
        QTimer.singleShot(150, self._remove_invisible_shake_border)
        self._set_next_shake_flash_interval()

    def _restore_shake_flash(self):
        pass

        # Scanline effect: overlay widget with lines
        if getattr(self, 'effect_scanline', False):
            if not hasattr(self, '_scanline_overlay'):
                self._scanline_overlay = ScanlineOverlay(self.terminal)
                self._scanline_overlay.setParent(self.terminal.viewport())
                self._scanline_overlay.raise_()
            self._scanline_overlay.resize(self.terminal.viewport().size())
            self._scanline_overlay.show()
        else:
            if hasattr(self, '_scanline_overlay'):
                self._scanline_overlay.hide()

        # Glitch effect: animated character glitch
        if getattr(self, 'effect_glitch', False):
            if not hasattr(self, '_glitch_timer'):
                self._glitch_timer = QTimer(self)
                self._glitch_timer.timeout.connect(self._do_glitch)
            self._set_next_glitch_interval()
            # Glitch shake effect: rare shake of the terminal widget
            if not hasattr(self, '_shake_timer'):
                self._shake_timer = QTimer(self)
                self._shake_timer.timeout.connect(self._do_shake)
            self._set_next_shake_interval()
        else:
            if hasattr(self, '_glitch_timer'):
                self._glitch_timer.stop()
                del self._glitch_timer
            if hasattr(self, '_glitching') and self._glitching:
                self._restore_terminal_text()
            if hasattr(self, '_shake_timer'):
                self._shake_timer.stop()
                del self._shake_timer

    def _set_next_shake_interval(self):
        import random
        if hasattr(self, '_shake_timer'):
            interval = random.randint(3000, 5000)  # 3 to 5 seconds for testing
            self._shake_timer.start(interval)

    def _do_shake(self):
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect
        orig_geom = self.terminal.geometry()
        anim = QPropertyAnimation(self.terminal, b'geometry', self)
        shake_geoms = [orig_geom]
        for dx in [-10, 10, -7, 7, -4, 4, 0]:
            shake_geoms.append(QRect(orig_geom.x() + dx, orig_geom.y(), orig_geom.width(), orig_geom.height()))
        anim.setDuration(300)
        anim.setKeyValueAt(0, shake_geoms[0])
        anim.setKeyValueAt(0.15, shake_geoms[1])
        anim.setKeyValueAt(0.45, shake_geoms[3])
        anim.setKeyValueAt(0.6, shake_geoms[4])
        anim.setKeyValueAt(0.75, shake_geoms[5])
        anim.setKeyValueAt(1, shake_geoms[6])
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.finished.connect(lambda: self.terminal.setGeometry(orig_geom))
        anim.start()
        self._set_next_shake_interval()

    def _apply_invisible_shake_border(self):
        # Apply a border with the same color as the background so the text shifts but border is invisible
        style = self.terminal.styleSheet()
        if 'border: 2px solid #101014;' not in style:
            self.terminal.setStyleSheet(style + 'border: 2px solid #101014;')

    def _remove_invisible_shake_border(self):
        # Remove the invisible border
        style = self.terminal.styleSheet().replace('border: 2px solid #101014;', '')
        self.terminal.setStyleSheet(style)

    def _set_next_shake_interval(self):
        import random
        if hasattr(self, '_shake_timer'):
            interval = random.randint(20000, 45000)  # 20 to 45 seconds
            self._shake_timer.start(interval)

    def _do_shake(self):
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        anim = QPropertyAnimation(self.terminal, b'pos', self)
        orig_pos = self.terminal.pos()
        shake_positions = [orig_pos]
        for dx in [-10, 10, -7, 7, -4, 4, 0]:
            shake_positions.append(orig_pos + Qt.QPoint(dx, 0))
        anim.setDuration(300)
        anim.setKeyValueAt(0, shake_positions[0])
        anim.setKeyValueAt(0.15, shake_positions[1])
        anim.setKeyValueAt(0.3, shake_positions[2])
        anim.setKeyValueAt(0.45, shake_positions[3])
        anim.setKeyValueAt(0.6, shake_positions[4])
        anim.setKeyValueAt(0.75, shake_positions[5])
        anim.setKeyValueAt(1, shake_positions[6])
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()
        self._set_next_shake_interval()
    def update_terminal_effects(self):
        # CRT effect: green text, bold font
        if getattr(self, 'effect_crt', False):
            self.terminal.setStyleSheet('background: #101014; color: #39ff14; font-family: Consolas; font-size: 14px; font-weight: bold;')
        else:
            self.terminal.setStyleSheet('background: #101014; color: #c0c0ff; font-family: Consolas; font-size: 14px;')

        # Scanline effect: overlay widget with lines
        if getattr(self, 'effect_scanline', False):
            if not hasattr(self, '_scanline_overlay'):
                self._scanline_overlay = ScanlineOverlay(self.terminal)
                self._scanline_overlay.setParent(self.terminal.viewport())
                self._scanline_overlay.raise_()
            self._scanline_overlay.resize(self.terminal.viewport().size())
            self._scanline_overlay.show()
        else:
            if hasattr(self, '_scanline_overlay'):
                self._scanline_overlay.hide()

        # Glitch effect: animated character glitch
        from PyQt6.QtCore import QTimer
        import random, string
        if getattr(self, 'effect_glitch', False):
            if not hasattr(self, '_glitch_timer'):
                self._glitch_timer = QTimer(self)
                self._glitch_timer.timeout.connect(self._do_glitch)
            self._set_next_glitch_interval()

    def _set_next_glitch_interval(self):
        import random
        if hasattr(self, '_glitch_timer'):
            interval = random.randint(3000, 15000)  # 3 to 15 seconds
            self._glitch_timer.start(interval)
            self._glitching = False
        else:
            if hasattr(self, '_glitch_timer'):
                self._glitch_timer.stop()
                del self._glitch_timer
            if hasattr(self, '_glitching') and self._glitching:
                self._restore_terminal_text()

    def _do_glitch(self):
        import random, string
        if not hasattr(self, '_original_text'):
            self._original_text = self.terminal.toPlainText()
        text = self.terminal.toPlainText()
        if not text.strip():
            return
        self._original_text = text
        # Save current scroll position
        scroll_bar = self.terminal.verticalScrollBar()
        scroll_pos = scroll_bar.value()
        lines = text.splitlines()
        glitch_chars = '█▓▒░@#$%&*?!/\\|><~'
        # Only glitch the last X lines
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
        # Restore scroll position
        scroll_bar.setValue(scroll_pos)
        self._glitching = True
        QTimer.singleShot(120, lambda: self._restore_terminal_text(scroll_pos))
        self._set_next_glitch_interval()

    def _restore_terminal_text(self, scroll_pos=None):
        if hasattr(self, '_original_text'):
            self.terminal.setPlainText(self._original_text)
            if scroll_pos is not None:
                self.terminal.verticalScrollBar().setValue(scroll_pos)
        self._glitching = False

    def open_effects_menu(self):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        menu = QMenu(self)
        crt_action = QAction('CRT Effect', self, checkable=True)
        crt_action.setChecked(self.effect_crt)
        scanline_action = QAction('Scanline Effect', self, checkable=True)
        scanline_action.setChecked(self.effect_scanline)
        glitch_action = QAction('Glitch Effect', self, checkable=True)
        glitch_action.setChecked(self.effect_glitch)
        shake_action = QAction('Shake Effect', self, checkable=True)
        shake_action.setChecked(getattr(self, 'effect_shake', False))

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
            if self.effect_shake:
                if not hasattr(self, '_shake_flash_timer'):
                    self._shake_flash_timer = QTimer(self)
                    self._shake_flash_timer.timeout.connect(self._do_shake_flash)
                self._set_next_shake_flash_interval()
            else:
                if hasattr(self, '_shake_flash_timer'):
                    self._shake_flash_timer.stop()
                    del self._shake_flash_timer
                # No red border to remove
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
    def __init__(self, parent=None):
        self.effect_shake = False
        super().__init__(parent)
        self.setMinimumSize(800, 400)
        layout = QVBoxLayout()
        # Terminal display
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet('background: #101014; color: #c0c0ff; font-family: Consolas; font-size: 14px;')
        self.terminal.setMaximumHeight(300)
        layout.addWidget(self.terminal)

        # Input row
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText('Type command and press Enter...')
        self.input.returnPressed.connect(self.run_command)
        input_row.addWidget(self.input)
        self.send_btn = QPushButton('Send')
        self.send_btn.clicked.connect(self.run_command)
        input_row.addWidget(self.send_btn)
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.terminal.clear)
        input_row.addWidget(self.clear_btn)
        layout.addLayout(input_row)

        # Settings row
        settings_row = QHBoxLayout()
        self.font_btn = QPushButton('Font')
        self.font_btn.clicked.connect(self.choose_font)
        settings_row.addWidget(self.font_btn)
        self.color_btn = QPushButton('Color')
        self.color_btn.clicked.connect(self.choose_color)
        settings_row.addWidget(self.color_btn)
        # Effects button
        self.effects_btn = QPushButton('Effects')
        self.effects_btn.clicked.connect(self.open_effects_menu)
        settings_row.addWidget(self.effects_btn)
        # Effects state
        self.effect_crt = False
        self.effect_scanline = False
        self.effect_glitch = False
        self.update_terminal_effects()

        # Shell detection
        self.shell_combo = QComboBox()
        shell_candidates = []
        if platform.system() == 'Windows':
            if shutil.which('cmd.exe'):
                shell_candidates.append('cmd.exe')
            if shutil.which('powershell.exe'):
                shell_candidates.append('powershell.exe')
        else:
            if shutil.which('bash'):
                shell_candidates.append('bash')
            if shutil.which('sh'):
                shell_candidates.append('sh')
        shell_options = []
        for shell in shell_candidates:
            try:
                if shell in ('cmd.exe', 'powershell.exe'):
                    result = subprocess.run([shell, '/c', 'echo', 'test'], capture_output=True, timeout=2)
                else:
                    result = subprocess.run([shell, '-c', 'echo test'], capture_output=True, timeout=2)
                if result.returncode == 0:
                    shell_options.append(shell)
            except Exception:
                continue
        if not shell_options:
            shell_options = ['cmd.exe'] if platform.system() == 'Windows' else ['bash']
        self.shell_combo.addItems(shell_options)
        self.shell_combo.currentIndexChanged.connect(self.change_shell)
        settings_row.addWidget(QLabel('Shell:'))
        settings_row.addWidget(self.shell_combo)
        settings_row.addStretch(1)
        layout.addLayout(settings_row)
        self.setLayout(layout)

        # Command history
        self.history = []
        self.history_index = 0
        self.input.installEventFilter(self)

        # QProcess for running shell
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.start_shell()

    def start_shell(self):
        shell = self.shell_combo.currentText()
        self.process.start(shell)
        self.terminal.appendPlainText(f'--- Started shell: {shell} ---')

    def change_shell(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.process.waitForFinished(1000)
        self.terminal.appendPlainText(f'--- Switching to shell: {self.shell_combo.currentText()} ---')
        self.start_shell()

    def run_command(self):
        cmd = self.input.text().strip()
        if not cmd or not self.process.state() == QProcess.ProcessState.Running:
            return
        self.terminal.appendPlainText(f'> {cmd}')
        # If user types clear or cls, clear the terminal
        if cmd.lower() in ('clear', 'cls'):
            self.terminal.clear()
            self.input.clear()
            return
        self.process.write((cmd + '\n').encode())
        # Add to history
        if not self.history or (self.history and self.history[-1] != cmd):
            self.history.append(cmd)
        self.history_index = len(self.history)
        self.input.clear()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.terminal.appendPlainText(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        self.terminal.appendPlainText(data)

    def process_finished(self):
        self.terminal.appendPlainText('--- Shell exited ---')

    def choose_font(self):
        font, ok = QFontDialog.getFont(self.terminal.font(), self, 'Choose Terminal Font')
        if ok:
            self.terminal.setFont(font)

    def choose_color(self):
        color = QColorDialog.getColor(self.terminal.palette().color(self.terminal.foregroundRole()), self, 'Choose Text Color')
        if color.isValid():
            self.terminal.setStyleSheet(f'background: #101014; color: {color.name()};')

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                if self.history and self.history_index > 0:
                    self.history_index -= 1
                    self.input.setText(self.history[self.history_index])
                return True
            elif event.key() == Qt.Key.Key_Down:
                if self.history and self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input.setText(self.history[self.history_index])
                else:
                    self.history_index = len(self.history)
                    self.input.clear()
                return True
        return super().eventFilter(obj, event)
