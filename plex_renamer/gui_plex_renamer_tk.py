# plex_renamer/gui_pyqt.py
from pathlib import Path
import threading
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QFileDialog, QCheckBox, QLabel,
    QProgressBar
)
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from plex_renamer.core import run_renamer


class LogEmitter(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)


class PlexRenamerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plex Renamer")
        self.resize(800, 500)

        self.emitter = LogEmitter()
        self.emitter.log.connect(self.append_log)
        self.emitter.progress.connect(self.update_progress)

        self.stop_event = threading.Event()

        # Path input + choose button
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Выберите файл или папку...")
        self.path_edit.setAcceptDrops(True)
        self.path_edit.dragEnterEvent = self.dragEnterEvent
        self.path_edit.dropEvent = self.dropEvent

        self.choose_btn = QPushButton("Выбрать")
        self.choose_btn.clicked.connect(self.choose_path)
        path_layout.addWidget(QLabel("Путь:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.choose_btn)

        # Options
        opts_layout = QHBoxLayout()
        self.apply_check = QCheckBox("Применить изменения (--apply)")
        opts_layout.addWidget(self.apply_check)
        opts_layout.addStretch()

        # Buttons start/stop
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Запустить")
        self.start_btn.clicked.connect(self.start_worker)
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.request_stop)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Log window
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(path_layout)
        main_layout.addLayout(opts_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(QLabel("Прогресс:"))
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("Лог:"))
        main_layout.addWidget(self.log)
        self.setLayout(main_layout)

    # drag & drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.path_edit.setText(urls[0].toLocalFile())

    # GUI callbacks
    def append_log(self, text: str):
        self.log.append(text)

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def choose_path(self):
        dialog = QFileDialog(self, "Выберите файл или папку")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                path = selected[0]
                self.path_edit.setText(path)

    def start_worker(self):
        path = self.path_edit.text().strip()
        if not path:
            self.append_log("❌ Укажите путь до файла или папки.")
            return

        apply_flag = self.apply_check.isChecked()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.choose_btn.setEnabled(False)
        self.apply_check.setEnabled(False)
        self.progress_bar.setValue(0)
        self.stop_event.clear()

        t = threading.Thread(target=self._worker_thread,
                             args=(path, apply_flag), daemon=True)
        t.start()

    def request_stop(self):
        self.append_log("⏳ Запрошена остановка...")
        self.stop_event.set()

    def _worker_thread(self, path: str, apply_flag: bool):
        def cb(message: str = None, progress: int = None):
            if message:
                self.emitter.log.emit(str(message))
            if progress is not None:
                self.emitter.progress.emit(progress)

        try:
            self.emitter.log.emit(
                f"Начало обработки: {path}  apply={apply_flag}")
            run_renamer(path, apply=apply_flag, callback=cb,
                        stop_flag=self.stop_event)
            self.emitter.log.emit("✅ Работа завершена.")
        except Exception as e:
            self.emitter.log.emit(f"❗ Ошибка: {e}")
        finally:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self._reenable_ui)

    def _reenable_ui(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.choose_btn.setEnabled(True)
        self.apply_check.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    w = PlexRenamerGUI()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
