#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QPushButton, QLineEdit, 
                             QTextEdit, QFileDialog, QProgressBar, QTabWidget, 
                             QListWidget, QListWidgetItem, QMessageBox, 
                             QGroupBox, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..organizer import MediaOrganizerWorker
from .styles import ModernStyles

class ModernMediaOrganizer(QMainWindow):
    """现代化媒体整理器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.apply_modern_style()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("媒体整理器 v7.0 - 现代化GUI")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("📁 媒体整理器")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(ModernStyles.get_title_style())
        main_layout.addWidget(title_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(ModernStyles.get_tab_style())
        
        # 整理选项卡
        self.organize_tab = self.create_organize_tab()
        self.tab_widget.addTab(self.organize_tab, "📂 文件整理")
        
        # 预览选项卡
        self.preview_tab = self.create_preview_tab()
        self.tab_widget.addTab(self.preview_tab, "��️ 文件预览")
        
        # 设置选项卡
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def create_organize_tab(self):
        """创建整理选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 源文件夹选择
        source_group = QGroupBox("📁 源文件夹")
        source_group.setStyleSheet(ModernStyles.get_group_style())
        source_layout = QHBoxLayout(source_group)
        
        self.source_path = QLineEdit()
        self.source_path.setPlaceholderText("选择要整理的文件夹...")
        self.source_path.setStyleSheet(ModernStyles.get_input_style())
        
        self.source_btn = QPushButton("浏览")
        self.source_btn.setStyleSheet(ModernStyles.get_button_style())
        self.source_btn.clicked.connect(self.select_source_folder)
        
        source_layout.addWidget(self.source_path)
        source_layout.addWidget(self.source_btn)
        layout.addWidget(source_group)
        
        # 目标文件夹选择
        target_group = QGroupBox("🎯 目标文件夹")
        target_group.setStyleSheet(ModernStyles.get_group_style())
        target_layout = QHBoxLayout(target_group)
        
        self.target_path = QLineEdit()
        self.target_path.setPlaceholderText("选择整理后的文件存放位置...")
        self.target_path.setStyleSheet(ModernStyles.get_input_style())
        
        self.target_btn = QPushButton("浏览")
        self.target_btn.setStyleSheet(ModernStyles.get_button_style())
        self.target_btn.clicked.connect(self.select_target_folder)
        
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(self.target_btn)
        layout.addWidget(target_group)
        
        # 整理选项
        options_group = QGroupBox("⚙️ 整理选项")
        options_group.setStyleSheet(ModernStyles.get_group_style())
        options_layout = QGridLayout(options_group)
        
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
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 开始整理")
        self.start_btn.setStyleSheet(ModernStyles.get_primary_button_style())
        self.start_btn.clicked.connect(self.start_organizing)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet(ModernStyles.get_danger_button_style())
        self.stop_btn.clicked.connect(self.stop_organizing)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 日志区域
        log_group = QGroupBox("📋 操作日志")
        log_group.setStyleSheet(ModernStyles.get_group_style())
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet(ModernStyles.get_log_style())
        
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        return tab
        
    def create_preview_tab(self):
        """创建预览选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(ModernStyles.get_list_style())
        
        layout.addWidget(QLabel("📋 文件预览"))
        layout.addWidget(self.file_list)
        
        return tab
        
    def create_settings_tab(self):
        """创建设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 主题设置
        theme_group = QGroupBox("🎨 主题设置")
        theme_group.setStyleSheet(ModernStyles.get_group_style())
        theme_layout = QHBoxLayout(theme_group)
        
        theme_layout.addWidget(QLabel("主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认", "深色", "浅色"])
        self.theme_combo.setStyleSheet(ModernStyles.get_input_style())
        
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addWidget(theme_group)
        
        # 文件类型设置
        filetype_group = QGroupBox("📄 支持的文件类型")
        filetype_group.setStyleSheet(ModernStyles.get_group_style())
        filetype_layout = QVBoxLayout(filetype_group)
        
        self.image_check = QCheckBox("图片文件 (.jpg, .png, .gif 等)")
        self.image_check.setChecked(True)
        self.video_check = QCheckBox("视频文件 (.mp4, .avi, .mkv 等)")
        self.video_check.setChecked(True)
        self.audio_check = QCheckBox("音频文件 (.mp3, .wav, .flac 等)")
        self.audio_check.setChecked(True)
        self.doc_check = QCheckBox("文档文件 (.pdf, .doc, .txt 等)")
        self.doc_check.setChecked(True)
        
        filetype_layout.addWidget(self.image_check)
        filetype_layout.addWidget(self.video_check)
        filetype_layout.addWidget(self.audio_check)
        filetype_layout.addWidget(self.doc_check)
        
        layout.addWidget(filetype_group)
        
        layout.addStretch()
        
        return tab
        
    def apply_modern_style(self):
        """应用现代化样式"""
        self.setStyleSheet(ModernStyles.get_main_style())
        
    def select_source_folder(self):
        """选择源文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if folder:
            self.source_path.setText(folder)
            self.scan_files()
            
    def select_target_folder(self):
        """选择目标文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            self.target_path.setText(folder)
            
    def scan_files(self):
        """扫描文件"""
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
        """开始整理"""
        source_dir = self.source_path.text()
        target_dir = self.target_path.text()
        
        if not source_dir or not target_dir:
            QMessageBox.warning(self, "警告", "请选择源文件夹和目标文件夹！")
            return
            
        if not os.path.exists(source_dir):
            QMessageBox.warning(self, "警告", "源文件夹不存在！")
            return
            
        # 创建目标文件夹
        os.makedirs(target_dir, exist_ok=True)
        
        # 启动工作线程
        self.worker = MediaOrganizerWorker(
            source_dir, target_dir,
            self.organize_by_date.isChecked(),
            self.organize_by_type.isChecked(),
            self.create_subfolders.isChecked()
        )
        
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_bar.showMessage)
        self.worker.status.connect(self.log_text.append)
        self.worker.finished.connect(self.organizing_finished)
        self.worker.error.connect(self.show_error)
        
        self.worker.start()
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def stop_organizing(self):
        """停止整理"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            
        self.organizing_finished()
        
    def organizing_finished(self):
        """整理完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("就绪")
        
    def show_error(self, error_msg):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", error_msg)
        self.organizing_finished()
