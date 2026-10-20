import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QLineEdit, QComboBox, QProgressBar,
    QMessageBox, QTextEdit, QGroupBox, QGridLayout, QSpinBox, QCheckBox, QFormLayout,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import ffmpeg
from PIL import Image
import zipfile
import py7zr
import shutil
import tempfile
import subprocess
import platform
from Files.auto_manager import autom, autom_off, clear_recycle_bin
from Files.temp_clr import clear_temp

class ConversionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class PCManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.active_workers = []
        self.is_processing = False
        self.last_split_folder = None
        self.setWindowTitle("Oayan AI PC Manager")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui()

    def closeEvent(self, event):
        for worker in self.active_workers:
            worker.quit()
            worker.wait()
        event.accept()

    def get_dark_theme(self):
        return """
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1e1e, stop:1 #2d2d2d);
                color: #ffffff;
            }
            QWidget {
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #444;
                background-color: #252526;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3c3c3c, stop:1 #4c4c4c);
                color: #fff;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005a9e);
                color: #fff;
            }
            QTabBar::tab:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4c4c4c, stop:1 #5c5c5c);
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5a52);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5252, stop:1 #d43f3f);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #cc4444, stop:1 #aa3333);
            }
            QPushButton[class="convert"] {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ecdc4, stop:1 #44a08d);
            }
            QPushButton[class="convert"]:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #26d0ce, stop:1 #2e8b57);
            }
            QPushButton[class="extract"] {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffe66d, stop:1 #ffb74d);
            }
            QPushButton[class="extract"]:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffeb3b, stop:1 #ff9800);
            }
            QPushButton[class="system"] {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a29bfe, stop:1 #6c5ce7);
            }
            QPushButton[class="system"]:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8e44ad, stop:1 #5b2c6f);
            }
            QLineEdit, QComboBox {
                background-color: #3c3c3c;
                color: #fff;
                border: 2px solid #555;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #007acc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #fff;
                font-size: 16px;
            }
            QLabel {
                color: #fff;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                width: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Oayan AI PC Manager")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Progress and Status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #007acc; font-weight: bold;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Audio Tools Tab
        audio_tab = self.create_audio_tab()
        self.tab_widget.addTab(audio_tab, "Audio Tools")

        # Video Tools Tab
        video_tab = self.create_video_tab()
        self.tab_widget.addTab(video_tab, "Video Tools")

        # Image Tools Tab
        image_tab = self.create_image_tab()
        self.tab_widget.addTab(image_tab, "Image Tools")

        # Archive Tools Tab
        archive_tab = self.create_archive_tab()
        self.tab_widget.addTab(archive_tab, "Archive Tools")

        # System Tools Tab
        system_tab = self.create_system_tab()
        self.tab_widget.addTab(system_tab, "System Tools")

        # Footer
        footer = QLabel("Owner: Muhammad Ayan | All Rights Reserved | Backed By Oayan")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(footer)

    def create_audio_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        scroll.setWidget(widget)
        layout = QVBoxLayout(widget)

        group = QGroupBox("Audio Conversion")
        form_layout = QFormLayout(group)

        self.audio_input = QLineEdit()
        self.audio_input.setPlaceholderText("Select input audio file")
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.audio_input)
        browse_audio_input = QPushButton("Browse")
        browse_audio_input.clicked.connect(lambda: self.browse_file(self.audio_input, "Audio Files (*.mp3 *.m4a *.wav *.flac *.aac)"))
        input_layout.addWidget(browse_audio_input)
        form_layout.addRow("Input File:", input_layout)

        self.audio_output = QLineEdit()
        self.audio_output.setPlaceholderText("Select output path")
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.audio_output)
        browse_audio_output = QPushButton("Browse")
        browse_audio_output.clicked.connect(lambda: self.browse_save_file(self.audio_output, "Audio Files (*.mp3 *.m4a *.wav *.flac *.aac)"))
        output_layout.addWidget(browse_audio_output)
        form_layout.addRow("Output File:", output_layout)

        self.audio_format = QComboBox()
        self.audio_format.addItems(["mp3", "m4a", "wav", "flac", "aac"])
        form_layout.addRow("Format:", self.audio_format)

        convert_audio_btn = QPushButton("Convert Audio 🎵")
        convert_audio_btn.setProperty("class", "convert")
        convert_audio_btn.clicked.connect(self.convert_audio)
        form_layout.addRow("", convert_audio_btn)

        self.open_audio_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_audio_folder_btn.setProperty("class", "system")
        self.open_audio_folder_btn.clicked.connect(lambda: self.open_output_folder(self.audio_output.text()))
        form_layout.addRow("", self.open_audio_folder_btn)

        layout.addWidget(group)

        # Video to Audio
        group2 = QGroupBox("Video to Audio")
        form_layout2 = QFormLayout(group2)

        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Select video file")
        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_input)
        browse_video_input = QPushButton("Browse")
        browse_video_input.clicked.connect(lambda: self.browse_file(self.video_input, "Video Files (*.mp4 *.avi *.mkv *.mov)"))
        video_layout.addWidget(browse_video_input)
        form_layout2.addRow("Video File:", video_layout)

        self.audio_from_video_output = QLineEdit()
        self.audio_from_video_output.setPlaceholderText("Select output audio path")
        audio_out_layout = QHBoxLayout()
        audio_out_layout.addWidget(self.audio_from_video_output)
        browse_audio_from_video_output = QPushButton("Browse")
        browse_audio_from_video_output.clicked.connect(lambda: self.browse_save_file(self.audio_from_video_output, "Audio Files (*.mp3 *.m4a *.wav)"))
        audio_out_layout.addWidget(browse_audio_from_video_output)
        form_layout2.addRow("Output Audio:", audio_out_layout)

        self.audio_from_video_format = QComboBox()
        self.audio_from_video_format.addItems(["mp3", "m4a", "wav"])
        form_layout2.addRow("Format:", self.audio_from_video_format)

        extract_audio_btn = QPushButton("Extract Audio 🎶")
        extract_audio_btn.setProperty("class", "extract")
        extract_audio_btn.clicked.connect(self.extract_audio_from_video)
        form_layout2.addRow("", extract_audio_btn)

        self.open_video_audio_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_video_audio_folder_btn.setProperty("class", "system")
        self.open_video_audio_folder_btn.clicked.connect(lambda: self.open_output_folder(self.audio_from_video_output.text()))
        form_layout2.addRow("", self.open_video_audio_folder_btn)

        layout.addWidget(group2)

        # Audio Splitter
        group3 = QGroupBox("Audio Splitter")
        form_layout3 = QFormLayout(group3)

        self.split_input = QLineEdit()
        self.split_input.setPlaceholderText("Select audio file to split")
        split_layout = QHBoxLayout()
        split_layout.addWidget(self.split_input)
        browse_split_input = QPushButton("Browse")
        browse_split_input.clicked.connect(lambda: self.browse_file(self.split_input, "Audio Files (*.mp3 *.m4a *.wav *.flac *.aac)"))
        split_layout.addWidget(browse_split_input)
        form_layout3.addRow("Audio File:", split_layout)

        self.split_output_folder = QLineEdit()
        self.split_output_folder.setPlaceholderText("Leave empty to save next to the source file")
        split_output_layout = QHBoxLayout()
        split_output_layout.addWidget(self.split_output_folder)
        browse_split_output = QPushButton("Browse")
        browse_split_output.clicked.connect(lambda: self.browse_folder(self.split_output_folder))
        split_output_layout.addWidget(browse_split_output)
        form_layout3.addRow("Output Folder:", split_output_layout)

        duration_layout = QHBoxLayout()
        self.split_h = QSpinBox()
        self.split_h.setRange(0, 23)
        self.split_h.setSuffix(" h")
        self.split_m = QSpinBox()
        self.split_m.setRange(0, 59)
        self.split_m.setSuffix(" m")
        self.split_m.setValue(10)  # Default 10 min
        self.split_s = QSpinBox()
        self.split_s.setRange(0, 59)
        self.split_s.setSuffix(" s")
        
        duration_layout.addWidget(self.split_h)
        duration_layout.addWidget(self.split_m)
        duration_layout.addWidget(self.split_s)
        form_layout3.addRow("Split Every:", duration_layout)

        split_audio_btn = QPushButton("Split Audio ✂️")
        split_audio_btn.setProperty("class", "extract")
        split_audio_btn.clicked.connect(self.split_audio)
        form_layout3.addRow("", split_audio_btn)

        self.open_split_folder_btn = QPushButton("Open Splits Folder 📁")
        self.open_split_folder_btn.setProperty("class", "system")
        self.open_split_folder_btn.clicked.connect(self.open_last_split_folder)
        form_layout3.addRow("", self.open_split_folder_btn)

        layout.addWidget(group3)
        layout.addStretch()
        return scroll

    def create_video_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Video Conversion")
        form_layout = QFormLayout(group)

        self.video_conv_input = QLineEdit()
        self.video_conv_input.setPlaceholderText("Select input video file")
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.video_conv_input)
        browse_video_conv_input = QPushButton("Browse")
        browse_video_conv_input.clicked.connect(lambda: self.browse_file(self.video_conv_input, "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"))
        input_layout.addWidget(browse_video_conv_input)
        form_layout.addRow("Input File:", input_layout)

        self.video_conv_output = QLineEdit()
        self.video_conv_output.setPlaceholderText("Select output path")
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.video_conv_output)
        browse_video_conv_output = QPushButton("Browse")
        browse_video_conv_output.clicked.connect(lambda: self.browse_save_file(self.video_conv_output, "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"))
        output_layout.addWidget(browse_video_conv_output)
        form_layout.addRow("Output File:", output_layout)

        self.video_format = QComboBox()
        self.video_format.addItems(["mp4", "avi", "mkv", "mov", "wmv"])
        form_layout.addRow("Format:", self.video_format)

        convert_video_btn = QPushButton("Convert Video 🎥")
        convert_video_btn.setProperty("class", "convert")
        convert_video_btn.clicked.connect(self.convert_video)
        form_layout.addRow("", convert_video_btn)

        self.open_video_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_video_folder_btn.setProperty("class", "system")
        self.open_video_folder_btn.clicked.connect(lambda: self.open_output_folder(self.video_conv_output.text()))
        form_layout.addRow("", self.open_video_folder_btn)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def create_image_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Image Conversion")
        form_layout = QFormLayout(group)

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Select input image file")
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.image_input)
        browse_image_input = QPushButton("Browse")
        browse_image_input.clicked.connect(lambda: self.browse_file(self.image_input, "Image Files (*.png *.jpg *.jpeg *.ico *.bmp *.gif *.webp)"))
        input_layout.addWidget(browse_image_input)
        form_layout.addRow("Input File:", input_layout)

        self.image_output = QLineEdit()
        self.image_output.setPlaceholderText("Select output path")
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.image_output)
        browse_image_output = QPushButton("Browse")
        browse_image_output.clicked.connect(lambda: self.browse_save_file(self.image_output, "Image Files (*.png *.jpg *.jpeg *.ico *.bmp *.gif *.webp)"))
        output_layout.addWidget(browse_image_output)
        form_layout.addRow("Output File:", output_layout)

        self.image_format = QComboBox()
        self.image_format.addItems(["png", "jpg", "jpeg", "ico", "bmp", "gif", "webp"])
        form_layout.addRow("Format:", self.image_format)

        convert_image_btn = QPushButton("Convert Image 🖼️")
        convert_image_btn.setProperty("class", "convert")
        convert_image_btn.clicked.connect(self.convert_image)
        form_layout.addRow("", convert_image_btn)

        self.open_image_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_image_folder_btn.setProperty("class", "system")
        self.open_image_folder_btn.clicked.connect(lambda: self.open_output_folder(self.image_output.text()))
        form_layout.addRow("", self.open_image_folder_btn)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def create_archive_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Extract
        group1 = QGroupBox("Extract Archive")
        form_layout1 = QFormLayout(group1)

        self.archive_input = QLineEdit()
        self.archive_input.setPlaceholderText("Select archive file")
        archive_layout = QHBoxLayout()
        archive_layout.addWidget(self.archive_input)
        browse_archive_input = QPushButton("Browse")
        browse_archive_input.clicked.connect(lambda: self.browse_file(self.archive_input, "Archive Files (*.zip *.7z *.rar *.tar.gz)"))
        archive_layout.addWidget(browse_archive_input)
        form_layout1.addRow("Archive File:", archive_layout)

        self.extract_output = QLineEdit()
        self.extract_output.setPlaceholderText("Select extraction folder")
        extract_layout = QHBoxLayout()
        extract_layout.addWidget(self.extract_output)
        browse_extract_output = QPushButton("Browse")
        browse_extract_output.clicked.connect(lambda: self.browse_folder(self.extract_output))
        extract_layout.addWidget(browse_extract_output)
        form_layout1.addRow("Output Folder:", extract_layout)

        extract_btn = QPushButton("Extract 📦")
        extract_btn.setProperty("class", "extract")
        extract_btn.clicked.connect(self.extract_archive)
        form_layout1.addRow("", extract_btn)

        self.open_extract_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_extract_folder_btn.setProperty("class", "system")
        self.open_extract_folder_btn.clicked.connect(lambda: self.open_output_folder(self.extract_output.text()))
        form_layout1.addRow("", self.open_extract_folder_btn)

        layout.addWidget(group1)

        # Compress
        group2 = QGroupBox("Compress Folder")
        form_layout2 = QFormLayout(group2)

        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("Select folder to compress")
        compress_layout = QHBoxLayout()
        compress_layout.addWidget(self.compress_input)
        browse_compress_input = QPushButton("Browse")
        browse_compress_input.clicked.connect(lambda: self.browse_folder(self.compress_input))
        compress_layout.addWidget(browse_compress_input)
        form_layout2.addRow("Folder:", compress_layout)

        self.compress_output = QLineEdit()
        self.compress_output.setPlaceholderText("Select output archive path")
        compress_out_layout = QHBoxLayout()
        compress_out_layout.addWidget(self.compress_output)
        browse_compress_output = QPushButton("Browse")
        browse_compress_output.clicked.connect(lambda: self.browse_save_file(self.compress_output, "Archive Files (*.zip *.7z)"))
        compress_out_layout.addWidget(browse_compress_output)
        form_layout2.addRow("Output Archive:", compress_out_layout)

        self.compress_format = QComboBox()
        self.compress_format.addItems(["zip", "7z"])
        form_layout2.addRow("Format:", self.compress_format)

        compress_btn = QPushButton("Compress 🗜️")
        compress_btn.setProperty("class", "convert")
        compress_btn.clicked.connect(self.compress_folder)
        form_layout2.addRow("", compress_btn)

        self.open_compress_folder_btn = QPushButton("Open Output Folder 📁")
        self.open_compress_folder_btn.setProperty("class", "system")
        self.open_compress_folder_btn.clicked.connect(lambda: self.open_output_folder(os.path.dirname(self.compress_output.text()) if self.compress_output.text() else ""))
        form_layout2.addRow("", self.open_compress_folder_btn)

        layout.addWidget(group2)
        layout.addStretch()
        return widget

    def create_system_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Basic system tools
        group = QGroupBox("System Tools")
        vbox = QVBoxLayout(group)

        clear_temp_btn = QPushButton("Clear Temporary Files 🗑️")
        clear_temp_btn.setProperty("class", "system")
        clear_temp_btn.clicked.connect(self.clear_temp_files)
        vbox.addWidget(clear_temp_btn)

        clear_recycle_btn = QPushButton("Clear Recycle Bin 🗂️")
        clear_recycle_btn.setProperty("class", "system")
        clear_recycle_btn.clicked.connect(self.clear_recycle_bin)
        vbox.addWidget(clear_recycle_btn)

        system_info_btn = QPushButton("Show System Info ℹ️")
        system_info_btn.setProperty("class", "system")
        system_info_btn.clicked.connect(self.show_system_info)
        vbox.addWidget(system_info_btn)

        layout.addWidget(group)

        # Download Manager
        group1 = QGroupBox("Download Manager")
        hbox = QHBoxLayout(group1)

        dm_on_btn = QPushButton("Turn ON Download Manager 🔄")
        dm_on_btn.setProperty("class", "system")
        dm_on_btn.clicked.connect(autom)
        hbox.addWidget(dm_on_btn)

        dm_off_btn = QPushButton("Turn OFF Download Manager ⏹️")
        dm_off_btn.setProperty("class", "system")
        dm_off_btn.clicked.connect(autom_off)
        hbox.addWidget(dm_off_btn)

        layout.addWidget(group1)

        # Additional tools
        group2 = QGroupBox("Additional Tools")
        vbox2 = QVBoxLayout(group2)

        screenshot_btn = QPushButton("Take Screenshot 📸")
        screenshot_btn.setProperty("class", "system")
        screenshot_btn.clicked.connect(self.take_screenshot)
        vbox2.addWidget(screenshot_btn)

        calculator_btn = QPushButton("Open Calculator 🧮")
        calculator_btn.setProperty("class", "system")
        calculator_btn.clicked.connect(self.open_calculator)
        vbox2.addWidget(calculator_btn)

        layout.addWidget(group2)
        layout.addStretch()
        return widget

    def browse_file(self, line_edit, filter_str):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter_str)
        if file_path:
            line_edit.setText(file_path)

    def open_output_folder(self, file_path):
        if not file_path:
            self.show_message("Error", "No output path specified.", QMessageBox.Icon.Warning)
            return

        try:
            normalized_path = os.path.normpath(file_path)
            if os.path.isdir(normalized_path):
                folder_path = normalized_path
            else:
                folder_path = os.path.dirname(normalized_path)

            if not folder_path or not os.path.exists(folder_path):
                self.show_message("Error", "Folder does not exist yet.", QMessageBox.Icon.Warning)
                return

            if platform.system() == "Windows":
                subprocess.Popen(["explorer", folder_path])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            self.show_message("Error", f"Could not open folder: {e}", QMessageBox.Icon.Warning)

    def browse_save_file(self, line_edit, filter_str):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", filter_str)
        if file_path:
            line_edit.setText(file_path)

    def browse_folder(self, line_edit):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            line_edit.setText(folder_path)

    def toggle_ui(self, enabled):
        self.is_processing = not enabled
        self.progress_bar.setVisible(not enabled)
        if not enabled:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        
        self.tab_widget.setEnabled(enabled)

    def start_worker(self, func, status_text, *args):
        self.toggle_ui(False)
        self.status_label.setText(status_text)

        worker = ConversionWorker(func, *args)
        self.active_workers.append(worker)
        worker.finished.connect(self.on_conversion_finished)
        worker.finished.connect(lambda _msg, w=worker: self.cleanup_worker(w))
        worker.start()

    def cleanup_worker(self, worker):
        if worker in self.active_workers:
            self.active_workers.remove(worker)
        
    def convert_audio(self):
        if self.is_processing:
            self.show_message("Info", "A task is already in progress.")
            return

        input_file = self.audio_input.text()
        output_file = self.audio_output.text()
        format_ = self.audio_format.currentText()

        if not input_file or not output_file:
            self.show_message("Error", "Please select input and output files.", QMessageBox.Icon.Warning)
            return

        output_file = os.path.splitext(output_file)[0] + f".{format_}"

        self.start_worker(self._convert_audio, "Converting Audio...", input_file, output_file)

    def on_conversion_finished(self, msg):
        self.toggle_ui(True)
        self.status_label.setText("Ready")
        
        if msg.startswith("SUCCESS_SPLIT|"):
            folder = msg.split("|")[1]
            self.last_split_folder = folder
            self.show_message("Result", f"Audio split successfully into folder:\n{folder}")
        else:
            self.show_message("Result", msg)

    def open_last_split_folder(self):
        if self.last_split_folder and os.path.exists(self.last_split_folder):
            self.open_output_folder(self.last_split_folder)
        else:
            self.show_message("Info", "No recent split folder found.", QMessageBox.Icon.Information)

    def _convert_audio(self, input_file, output_file):
        ext = os.path.splitext(output_file)[1].lower()
        codec_map = {
            '.mp3': 'libmp3lame',
            '.m4a': 'aac',
            '.wav': 'pcm_s16le',
            '.flac': 'flac',
            '.aac': 'aac'
        }
        audio_codec = codec_map.get(ext, 'copy')
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(stream, output_file, acodec=audio_codec)
        ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
        return "Audio converted successfully!"

    def extract_audio_from_video(self):
        if self.is_processing:
            self.show_message("Info", "A task is already in progress.")
            return

        input_file = self.video_input.text()
        output_file = self.audio_from_video_output.text()
        format_ = self.audio_from_video_format.currentText()

        if not input_file or not output_file:
            self.show_message("Error", "Please select input and output files.", QMessageBox.Icon.Warning)
            return

        output_file = os.path.splitext(output_file)[0] + f".{format_}"

        self.start_worker(self._extract_audio, "Extracting Audio...", input_file, output_file)

    def _extract_audio(self, input_file, output_file):
        ext = os.path.splitext(output_file)[1].lower()
        codec_map = {'.mp3': 'libmp3lame', '.m4a': 'aac', '.wav': 'pcm_s16le'}
        audio_codec = codec_map.get(ext, 'copy')
        stream = ffmpeg.input(input_file)
        audio = stream.audio
        stream = ffmpeg.output(audio, output_file, acodec=audio_codec)
        ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
        return "Audio extracted successfully!"

    def convert_video(self):
        if self.is_processing:
            self.show_message("Info", "A task is already in progress.")
            return

        input_file = self.video_conv_input.text()
        output_file = self.video_conv_output.text()
        format_ = self.video_format.currentText()

        if not input_file or not output_file:
            self.show_message("Error", "Please select input and output files.", QMessageBox.Icon.Warning)
            return

        output_file = os.path.splitext(output_file)[0] + f".{format_}"

        self.start_worker(self._convert_video, "Converting Video...", input_file, output_file)

    def _convert_video(self, input_file, output_file):
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(stream, output_file)
        ffmpeg.run(stream, overwrite_output=True)
        return "Video converted successfully!"

    def split_audio(self):
        if self.is_processing:
            self.show_message("Info", "A task is already in progress.")
            return

        input_file = self.split_input.text()
        if not input_file:
            self.show_message("Error", "Please select an audio file.", QMessageBox.Icon.Warning)
            return

        split_sec = self.split_h.value() * 3600 + self.split_m.value() * 60 + self.split_s.value()
        if split_sec <= 0:
            self.show_message("Error", "Please specify a valid split duration.", QMessageBox.Icon.Warning)
            return

        output_root = self.split_output_folder.text().strip()
        self.start_worker(self._split_audio, "Splitting Audio...", input_file, split_sec, output_root)

    def _split_audio(self, input_file, split_sec, output_root):
        try:
            probe = ffmpeg.probe(input_file)
            duration = float(probe['format']['duration'])

            file_dir = output_root or os.path.dirname(input_file)
            file_name = os.path.splitext(os.path.basename(input_file))[0]
            ext = os.path.splitext(input_file)[1]

            os.makedirs(file_dir, exist_ok=True)
            output_folder = os.path.join(file_dir, f"{file_name}_splits")
            os.makedirs(output_folder, exist_ok=True)

            parts = int(duration // split_sec)
            if duration % split_sec > 0:
                parts += 1

            for i in range(parts):
                start_time = i * split_sec
                output_part = os.path.join(output_folder, f"{file_name}_part{i+1}{ext}")

                stream = ffmpeg.input(input_file, ss=start_time)
                if i < parts - 1:
                    stream = ffmpeg.output(stream, output_part, t=split_sec, acodec='copy')
                else:
                    stream = ffmpeg.output(stream, output_part, acodec='copy')

                ffmpeg.run(stream, overwrite_output=True)

            return f"SUCCESS_SPLIT|{output_folder}"
        except Exception as e:
            return f"Error splitting audio: {str(e)}"

    def convert_image(self):
        input_file = self.image_input.text()
        output_file = self.image_output.text()
        format_ = self.image_format.currentText()

        if not input_file or not output_file:
            self.show_message("Error", "Please select input and output files.", QMessageBox.Icon.Warning)
            return

        output_file = os.path.splitext(output_file)[0] + f".{format_}"

        try:
            from PIL import Image
            img = Image.open(input_file)
            
            # Convert to RGB if saving to format that doesn't support transparency like JPEG
            if format_.lower() in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            if format_.lower() == 'ico':
                # For ICO, we might need to specify sizes or it might just save directly
                img.save(output_file, format='ICO')
            else:
                img.save(output_file)
            
            self.show_message("Success", "Image converted successfully!")
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Warning)

    def extract_archive(self):
        archive_file = self.archive_input.text()
        output_folder = self.extract_output.text()

        if not archive_file or not output_folder:
            self.show_message("Error", "Please select archive and output folder.", QMessageBox.Icon.Warning)
            return

        try:
            if archive_file.endswith('.zip'):
                with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(output_folder)
            elif archive_file.endswith('.7z'):
                with py7zr.SevenZipFile(archive_file, mode='r') as z:
                    z.extractall(output_folder)
            else:
                self.show_message("Error", "Unsupported archive format.", QMessageBox.Icon.Warning)
                return
            self.show_message("Success", "Archive extracted successfully!")
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Warning)

    def compress_folder(self):
        input_folder = self.compress_input.text()
        output_file = self.compress_output.text()
        format_ = self.compress_format.currentText()

        if not input_folder or not output_file:
            self.show_message("Error", "Please select input folder and output file.", QMessageBox.Icon.Warning)
            return

        output_file = os.path.splitext(output_file)[0] + f".{format_}"

        try:
            if format_ == 'zip':
                shutil.make_archive(output_file.replace('.zip', ''), 'zip', input_folder)
            elif format_ == '7z':
                with py7zr.SevenZipFile(output_file, 'w') as archive:
                    archive.writeall(input_folder, arcname=os.path.basename(input_folder))
            self.show_message("Success", "Folder compressed successfully!")
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Warning)

    def clear_temp_files(self):
        result = clear_temp()
        if result:
            QMessageBox.warning(self, "Error", result)
        else:
            QMessageBox.information(self, "Success", "Temporary files cleared!")

    def clear_recycle_bin(self):
        try:
            clear_recycle_bin()
            self.show_message("Success", "Recycle bin cleared!")
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Warning)

    def show_system_info(self):
        info = f"OS: {platform.system()} {platform.release()}\n"
        info += f"Processor: {platform.processor()}\n"
        info += f"Python: {sys.version}"
        self.show_message("System Info", info)

    def take_screenshot(self):
        # Simple screenshot using pyautogui if available, else placeholder
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png)")
            if file_path:
                screenshot.save(file_path)
                self.show_message("Success", "Screenshot saved!")
        except ImportError:
            self.show_message("Error", "pyautogui not installed. Install it to use screenshot feature.", QMessageBox.Icon.Warning)

    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        msg_box.exec()

    def open_calculator(self):
        try:
            if platform.system() == 'Windows':
                subprocess.run(['calc'])
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Warning)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PCManagementApp()
    window.show()
    sys.exit(app.exec())
