#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config import SETTINGS
from media_organizer import MediaToolkit
import os
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
							 QGridLayout, QLabel, QPushButton, QLineEdit,
							 QTextEdit, QFileDialog, QProgressBar, QTabWidget,
							 QListWidget, QListWidgetItem, QMessageBox,
							 QGroupBox, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from organizer import MediaOrganizerWorker
from ui.styles import ModernStyles

class ModernMediaOrganizer(QMainWindow):
	def __init__(self, scale=1.0):
		super().__init__()
		self.scale = scale
		self.worker = None
		self.init_ui()
		self.apply_modern_style()

	def init_ui(self):
		s = self.scale
		self.setWindowTitle("媒体整理器 v7.0 - 现代化GUI")
		self.resize(int(1200*s), int(800*s))
		self.setMinimumSize(int(1000*s), int(600*s))

		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		main_layout = QVBoxLayout(central_widget)
		main_layout.setSpacing(int(20*s))
		main_layout.setContentsMargins(int(20*s), int(20*s), int(20*s), int(20*s))

		title_label = QLabel("📁 媒体整理器")
		title_label.setAlignment(Qt.AlignCenter)
		base_pt = self.font().pointSize() or 10
		title_font = QFont()
		title_font.setPointSize(int(base_pt * 2.6))
		title_font.setBold(True)
		title_label.setFont(title_font)
		title_label.setStyleSheet(ModernStyles.get_title_style(s))
		main_layout.addWidget(title_label)

		self.tab_widget = QTabWidget()
		self.tab_widget.setStyleSheet(ModernStyles.get_tab_style(s))

		self.organize_tab = self.create_organize_tab()
		self.tab_widget.addTab(self.organize_tab, "📂 文件整理")

		self.preview_tab = self.create_preview_tab()
		self.tab_widget.addTab(self.preview_tab, "👁️ 文件预览")

		self.settings_tab = self.create_settings_tab()
		self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")

		main_layout.addWidget(self.tab_widget)

		self.status_bar = self.statusBar()
		self.status_bar.showMessage("就绪")
		self.progress_bar = QProgressBar()
		self.progress_bar.setFixedHeight(int(18*s))
		self.progress_bar.setVisible(False)
		self.status_bar.addPermanentWidget(self.progress_bar)

	def create_organize_tab(self):
		s = self.scale
		tab = QWidget()
		layout = QVBoxLayout(tab)
		layout.setSpacing(int(15*s))

		source_group = QGroupBox("📁 源文件夹")
		source_group.setStyleSheet(ModernStyles.get_group_style(s))
		source_layout = QHBoxLayout(source_group)
		source_layout.setSpacing(int(8*s))

		self.source_path = QLineEdit()
		self.source_path.setPlaceholderText("选择要整理的文件夹...")
		self.source_path.setStyleSheet(ModernStyles.get_input_style(s))

		self.source_btn = QPushButton("浏览")
		self.source_btn.setStyleSheet(ModernStyles.get_button_style(s))
		self.source_btn.clicked.connect(self.select_source_folder)

		source_layout.addWidget(self.source_path)
		source_layout.addWidget(self.source_btn)
		layout.addWidget(source_group)

		target_group = QGroupBox("🎯 目标文件夹")
		target_group.setStyleSheet(ModernStyles.get_group_style(s))
		target_layout = QHBoxLayout(target_group)
		target_layout.setSpacing(int(8*s))

		self.target_path = QLineEdit()
		self.target_path.setPlaceholderText("选择整理后的文件存放位置...")
		self.target_path.setStyleSheet(ModernStyles.get_input_style(s))

		self.target_btn = QPushButton("浏览")
		self.target_btn.setStyleSheet(ModernStyles.get_button_style(s))
		self.target_btn.clicked.connect(self.select_target_folder)

		target_layout.addWidget(self.target_path)
		target_layout.addWidget(self.target_btn)
		layout.addWidget(target_group)

		options_group = QGroupBox("⚙️ 整理选项")
		options_group.setStyleSheet(ModernStyles.get_group_style(s))
		options_layout = QGridLayout(options_group)
		options_layout.setHorizontalSpacing(int(12*s))
		options_layout.setVerticalSpacing(int(8*s))

		self.organize_by_date = QCheckBox("按日期整理 (年/月)")
		self.organize_by_date.setChecked(True)
		self.organize_by_type = QCheckBox("按文件类型整理")
		self.organize_by_type.setChecked(True)
		self.create_subfolders = QCheckBox("自动创建子文件夹")
		self.create_subfolders.setChecked(True)

		options_layout.addWidget(self.organize_by_date, 0, 0)
		options_layout.addWidget(self.organize_by_type, 0, 1)
		options_layout.addWidget(self.create_subfolders, 1, 0)

		layout.addWidget(options_group)

		button_layout = QHBoxLayout()
		button_layout.setSpacing(int(10*s))

		self.start_btn = QPushButton("🚀 开始整理")
		self.start_btn.setStyleSheet(ModernStyles.get_primary_button_style(s))
		self.start_btn.clicked.connect(self.start_organizing)

		self.stop_btn = QPushButton("⏹️ 停止")
		self.stop_btn.setStyleSheet(ModernStyles.get_danger_button_style(s))
		self.stop_btn.clicked.connect(self.stop_organizing)
		self.stop_btn.setEnabled(False)

		button_layout.addWidget(self.start_btn)
		button_layout.addWidget(self.stop_btn)
		button_layout.addStretch()
		layout.addLayout(button_layout)

		log_group = QGroupBox("📋 操作日志")
		log_group.setStyleSheet(ModernStyles.get_group_style(s))
		log_layout = QVBoxLayout(log_group)
		log_layout.setContentsMargins(int(10*s), int(10*s), int(10*s), int(10*s))

		self.log_text = QTextEdit()
		self.log_text.setStyleSheet(ModernStyles.get_log_style(s))
		log_layout.addWidget(self.log_text)
		layout.addWidget(log_group)
		return tab

	def create_preview_tab(self):
		s = self.scale
		tab = QWidget()
		layout = QVBoxLayout(tab)
		layout.setSpacing(int(10*s))
		self.file_list = QListWidget()
		self.file_list.setStyleSheet(ModernStyles.get_list_style(s))
		layout.addWidget(QLabel("📋 文件预览"))
		layout.addWidget(self.file_list)
		return tab

	def create_settings_tab(self):
		s = self.scale
		tab = QWidget()
		layout = QVBoxLayout(tab)

		theme_group = QGroupBox("🎨 主题设置")
		theme_group.setStyleSheet(ModernStyles.get_group_style(s))
		theme_layout = QHBoxLayout(theme_group)
		theme_layout.setSpacing(int(8*s))
		theme_layout.addWidget(QLabel("主题:"))
		self.theme_combo = QComboBox()
		self.theme_combo.addItems(["默认", "深色", "浅色"])
		self.theme_combo.setStyleSheet(ModernStyles.get_input_style(s))
		theme_layout.addWidget(self.theme_combo)
		theme_layout.addStretch()
		layout.addWidget(theme_group)

		filetype_group = QGroupBox("📄 支持的文件类型")
		filetype_group.setStyleSheet(ModernStyles.get_group_style(s))
		filetype_layout = QVBoxLayout(filetype_group)

		self.image_check = QCheckBox("图片文件 (.jpg, .png, .gif 等)")
		self.video_check = QCheckBox("视频文件 (.mp4, .avi, .mkv 等)")
		self.audio_check = QCheckBox("音频文件 (.mp3, .wav, .flac 等)")
		self.doc_check = QCheckBox("文档文件 (.pdf, .doc, .txt 等)")
		for w in (self.image_check, self.video_check, self.audio_check, self.doc_check):
			w.setChecked(True)
			filetype_layout.addWidget(w)

		layout.addWidget(filetype_group)
		layout.addStretch()
		return tab

	def apply_modern_style(self):
		self.setStyleSheet(ModernStyles.get_main_style(self.scale))

	# 其余逻辑（选择目录、扫描、开始/停止、错误提示）保持不变…
	def select_source_folder(self):
		folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
		if folder:
			self.source_path.setText(folder)
			self.scan_files()

	def select_target_folder(self):
		folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
		if folder:
			self.target_path.setText(folder)

	def scan_files(self):
		source_dir = self.source_path.text()
		if not source_dir:
			return
		self.file_list.clear()
		self.log_text.append(f"正在扫描文件夹: {source_dir}")
		media_extensions = {
			'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
			'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
			'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
			'.pdf', '.doc', '.docx', '.txt', '.rtf'
		}
		file_count = 0
		for file_path in Path(source_dir).rglob('*'):
			if file_path.is_file() and file_path.suffix.lower() in media_extensions:
				item = QListWidgetItem(f"📄 {file_path.name}")
				item.setToolTip(str(file_path))
				self.file_list.addItem(item)
				file_count += 1
		self.log_text.append(f"找到 {file_count} 个媒体文件")

	def start_organizing(self):
		source_dir = self.source_path.text()
		target_dir = self.target_path.text()
		if not source_dir or not target_dir:
			QMessageBox.warning(self, "警告", "请选择源文件夹和目标文件夹！")
			return
		if not os.path.exists(source_dir):
			QMessageBox.warning(self, "警告", "源文件夹不存在！")
			return
		os.makedirs(target_dir, exist_ok=True)
		self.worker = MediaOrganizerWorker(
			source_dir, target_dir,
			self.organize_by_date.isChecked(),
			self.organize_by_type.isChecked(),
			self.create_subfolders.isChecked()
		)
		self.worker.progress.connect(self.progress_bar.setValue)
		self.worker.status.connect(self.statusBar().showMessage)
		self.worker.status.connect(self.log_text.append)
		self.worker.finished.connect(self.organizing_finished)
		self.worker.error.connect(self.show_error)
		self.worker.start()
		self.start_btn.setEnabled(False)
		self.stop_btn.setEnabled(True)
		self.progress_bar.setVisible(True)
		self.progress_bar.setValue(0)

	def stop_organizing(self):
		if self.worker:
			self.worker.stop()
			self.worker.wait()
		self.organizing_finished()

	def organizing_finished(self):
		self.start_btn.setEnabled(True)
		self.stop_btn.setEnabled(False)
		self.progress_bar.setVisible(False)
		self.statusBar().showMessage("就绪")

	def show_error(self, error_msg):
		QMessageBox.critical(self, "错误", error_msg)
		self.organizing_finished()
