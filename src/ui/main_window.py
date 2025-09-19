# src/ui/main_window.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import QScrollArea, QSizePolicy
from pathlib import Path
from PyQt5.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
	QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog, QProgressBar,
	QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
	QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from organizer import MediaOrganizerWorker
from ui.styles import ModernStyles
from config import SETTINGS
from media_organizer import MediaToolkit


class ModernMediaOrganizer(QMainWindow):
	def __init__(self, scale=1.0):
		super().__init__()
		self.scale = scale
		self.worker = None
		self.init_ui()
		self.apply_modern_style()
		self.tools = MediaToolkit(
			notify=lambda s: self.log_text.append(s),
			progress=self.progress_bar.setValue
		)

	def init_ui(self):
		s = self.scale
		self.setWindowTitle("媒体整理器 v7.0 - 现代化GUI")
		self.resize(int(1200*s), int(800*s))
		self.setMinimumSize(int(1000*s), int(600*s))

		central_widget = QWidget(); self.setCentralWidget(central_widget)
		main_layout = QVBoxLayout(central_widget)
		main_layout.setSpacing(int(20*s)); main_layout.setContentsMargins(int(20*s), int(20*s), int(20*s), int(20*s))

		title_label = QLabel("📁 媒体整理器"); title_label.setAlignment(Qt.AlignCenter)
		base_pt = self.font().pointSize() or 10
		title_font = QFont(); title_font.setPointSize(int(base_pt * 2.6)); title_font.setBold(True)
		title_label.setFont(title_font); title_label.setStyleSheet(ModernStyles.get_title_style(s))
		main_layout.addWidget(title_label)

		self.tab_widget = QTabWidget(); self.tab_widget.setStyleSheet(ModernStyles.get_tab_style(s))
		self.organize_tab = self.create_organize_tab(); self.tab_widget.addTab(self.organize_tab, "📂 文件整理")
		self.preview_tab = self.create_preview_tab(); self.tab_widget.addTab(self.preview_tab, "👁️ 文件预览")
		self.settings_tab = self.create_settings_tab(); self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")
		self.tools_tab = self.create_tools_tab(); self.tab_widget.addTab(self.tools_tab, "🧰 工具套件")
		main_layout.addWidget(self.tab_widget)

		self.status_bar = self.statusBar(); self.status_bar.showMessage("就绪")
		self.progress_bar = QProgressBar(); self.progress_bar.setFixedHeight(int(18*s))
		self.progress_bar.setVisible(False); self.status_bar.addPermanentWidget(self.progress_bar)

	def create_organize_tab(self):
		s = self.scale
		tab = QWidget(); layout = QVBoxLayout(tab); layout.setSpacing(int(15*s))

		source_group = QGroupBox("📁 源文件夹"); source_group.setStyleSheet(ModernStyles.get_group_style(s))
		source_layout = QHBoxLayout(source_group); source_layout.setSpacing(int(8*s))
		self.source_path = QLineEdit(); self.source_path.setPlaceholderText("选择要整理的文件夹..."); self.source_path.setStyleSheet(ModernStyles.get_input_style(s))
		self.source_btn = QPushButton("浏览"); self.source_btn.setStyleSheet(ModernStyles.get_button_style(s)); self.source_btn.clicked.connect(self.select_source_folder)
		source_layout.addWidget(self.source_path); source_layout.addWidget(self.source_btn); layout.addWidget(source_group)

		target_group = QGroupBox("🎯 目标文件夹"); target_group.setStyleSheet(ModernStyles.get_group_style(s))
		target_layout = QHBoxLayout(target_group); target_layout.setSpacing(int(8*s))
		self.target_path = QLineEdit(); self.target_path.setPlaceholderText("选择整理后的文件存放位置..."); self.target_path.setStyleSheet(ModernStyles.get_input_style(s))
		self.target_btn = QPushButton("浏览"); self.target_btn.setStyleSheet(ModernStyles.get_button_style(s)); self.target_btn.clicked.connect(self.select_target_folder)
		target_layout.addWidget(self.target_path); target_layout.addWidget(self.target_btn); layout.addWidget(target_group)

		options_group = QGroupBox("⚙️ 整理选项"); options_group.setStyleSheet(ModernStyles.get_group_style(s))
		options_layout = QGridLayout(options_group)
		options_layout.setHorizontalSpacing(int(12*s)); options_layout.setVerticalSpacing(int(8*s))
		self.organize_by_date = QCheckBox("按日期整理 (年/月)"); self.organize_by_date.setChecked(True)
		self.organize_by_type = QCheckBox("按文件类型整理"); self.organize_by_type.setChecked(True)
		self.create_subfolders = QCheckBox("自动创建子文件夹"); self.create_subfolders.setChecked(True)
		options_layout.addWidget(self.organize_by_date, 0, 0); options_layout.addWidget(self.organize_by_type, 0, 1); options_layout.addWidget(self.create_subfolders, 1, 0)
		layout.addWidget(options_group)

		button_layout = QHBoxLayout(); button_layout.setSpacing(int(10*s))
		self.start_btn = QPushButton("🚀 开始整理"); self.start_btn.setStyleSheet(ModernStyles.get_primary_button_style(s)); self.start_btn.clicked.connect(self.start_organizing)
		self.stop_btn = QPushButton("⏹️ 停止"); self.stop_btn.setStyleSheet(ModernStyles.get_danger_button_style(s)); self.stop_btn.clicked.connect(self.stop_organizing); self.stop_btn.setEnabled(False)
		button_layout.addWidget(self.start_btn); button_layout.addWidget(self.stop_btn); button_layout.addStretch()
		layout.addLayout(button_layout)

		log_group = QGroupBox("📋 操作日志"); log_group.setStyleSheet(ModernStyles.get_group_style(s))
		log_layout = QVBoxLayout(log_group); log_layout.setContentsMargins(int(10*s), int(10*s), int(10*s), int(10*s))
		self.log_text = QTextEdit(); self.log_text.setStyleSheet(ModernStyles.get_log_style(s))
		log_layout.addWidget(self.log_text); layout.addWidget(log_group)
		return tab

	def create_preview_tab(self):
		s = self.scale
		tab = QWidget(); layout = QVBoxLayout(tab); layout.setSpacing(int(10*s))
		self.file_list = QListWidget(); self.file_list.setStyleSheet(ModernStyles.get_list_style(s))
		layout.addWidget(QLabel("📋 文件预览")); layout.addWidget(self.file_list)
		return tab

	def create_settings_tab(self):
		s = self.scale
		tab = QWidget(); layout = QVBoxLayout(tab)
		theme_group = QGroupBox("🎨 主题设置"); theme_group.setStyleSheet(ModernStyles.get_group_style(s))
		theme_layout = QHBoxLayout(theme_group); theme_layout.setSpacing(int(8*s))
		theme_layout.addWidget(QLabel("主题:")); self.theme_combo = QComboBox(); self.theme_combo.addItems(["默认", "深色", "浅色"]); self.theme_combo.setStyleSheet(ModernStyles.get_input_style(s))
		theme_layout.addWidget(self.theme_combo); theme_layout.addStretch(); layout.addWidget(theme_group)

		filetype_group = QGroupBox("📄 支持的文件类型"); filetype_group.setStyleSheet(ModernStyles.get_group_style(s))
		filetype_layout = QVBoxLayout(filetype_group)
		self.image_check = QCheckBox("图片文件 (.jpg, .png, .gif 等)")
		self.video_check = QCheckBox("视频文件 (.mp4, .avi, .mkv 等)")
		self.audio_check = QCheckBox("音频文件 (.mp3, .wav, .flac 等)")
		self.doc_check = QCheckBox("文档文件 (.pdf, .doc, .txt 等)")
		for w in (self.image_check, self.video_check, self.audio_check, self.doc_check):
			w.setChecked(True); filetype_layout.addWidget(w)
		layout.addWidget(filetype_group); layout.addStretch()
		return tab

	def create_tools_tab(self):
	s = self.scale

	# 用滚动区承载内容，防止内容太多被压乱
	scroll = QScrollArea()
	scroll.setWidgetResizable(True)

	container = QWidget()
	layout = QVBoxLayout(container)
	layout.setSpacing(int(12*s))
	layout.setContentsMargins(int(12*s), int(12*s), int(12*s), int(12*s))

	# 通用 SizePolicy：输入框可扩展，按钮固定
	def conf_lineedit(le: QLineEdit):
		le.setStyleSheet(ModernStyles.get_input_style(s))
		le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
	def conf_button(btn: QPushButton, primary=False):
		btn.setStyleSheet(ModernStyles.get_primary_button_style(s) if primary else ModernStyles.get_button_style(s))
		btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

	# Topaz Poster 增强
	gb_topaz = QGroupBox("Topaz Poster 增强")
	gb_topaz.setStyleSheet(ModernStyles.get_group_style(s))
	l1 = QGridLayout(gb_topaz)

	self.topaz_src = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.topaz_src)
	self.topaz_work = QLineEdit(SETTINGS["IMAGE_SOURCE_DIR"]); conf_lineedit(self.topaz_work)
	btn_export = QPushButton("步骤1 导出并(可)启动Topaz"); conf_button(btn_export, primary=True); btn_export.clicked.connect(self.action_export_posters)
	btn_import = QPushButton("步骤2 导回增强Poster"); conf_button(btn_import); btn_import.clicked.connect(self.action_import_posters)

	r = 0
	l1.addWidget(QLabel("模板根:"), r, 0); l1.addWidget(self.topaz_src, r, 1)
	l1.addWidget(QLabel("工作目录:"), r, 2); l1.addWidget(self.topaz_work, r, 3)
	l1.addWidget(btn_export, r, 4); l1.addWidget(btn_import, r, 5)
	# 列伸展：输入框列扩展，按钮列不扩展
	for c in (1, 3):
		l1.setColumnStretch(c, 2)
	for c in (0, 2, 4, 5):
		l1.setColumnStretch(c, 0)

	layout.addWidget(gb_topaz)

	# ED2K 提取（自动解压）
	gb_ed2k = QGroupBox("ED2K 提取（自动解压）")
	gb_ed2k.setStyleSheet(ModernStyles.get_group_style(s))
	l2 = QGridLayout(gb_ed2k)

	self.ed2k_base = QLineEdit(SETTINGS["ED2K_SOURCE_DIR"]); conf_lineedit(self.ed2k_base)
	self.ed2k_out  = QLineEdit(SETTINGS["ED2K_OUTPUT_DIR"]); conf_lineedit(self.ed2k_out)
	self.ed2k_delete = QCheckBox("提取后删除TXT"); self.ed2k_delete.setChecked(True)
	btn_ed2k = QPushButton("开始提取"); conf_button(btn_ed2k, primary=True); btn_ed2k.clicked.connect(self.action_extract_ed2k)

	r = 0
	l2.addWidget(QLabel("来源:"), r, 0); l2.addWidget(self.ed2k_base, r, 1, 1, 2)
	l2.addWidget(QLabel("输出到:"), r, 3); l2.addWidget(self.ed2k_out, r, 4, 1, 2)
	l2.addWidget(self.ed2k_delete, r, 6); l2.addWidget(btn_ed2k, r, 7)
	l2.setColumnStretch(1, 2); l2.setColumnStretch(4, 2)
	for c in (0, 3, 6, 7):
		l2.setColumnStretch(c, 0)

	layout.addWidget(gb_ed2k)

	# 封面替换（按大小）
	gb_cover = QGroupBox("封面替换（按大小）")
	gb_cover.setStyleSheet(ModernStyles.get_group_style(s))
	l3 = QGridLayout(gb_cover)

	self.cover_repo   = QLineEdit(SETTINGS["COVER_SOURCE_DIR"]); conf_lineedit(self.cover_repo)
	self.cover_target = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.cover_target)
	btn_cover = QPushButton("开始替换"); conf_button(btn_cover, primary=True); btn_cover.clicked.connect(self.action_replace_covers)

	r = 0
	l3.addWidget(QLabel("封面库:"), r, 0); l3.addWidget(self.cover_repo, r, 1, 1, 3)
	l3.addWidget(QLabel("目标根:"), r, 4); l3.addWidget(self.cover_target, r, 5, 1, 3)
	l3.addWidget(btn_cover, r, 8)
	l3.setColumnStretch(1, 2); l3.setColumnStretch(5, 2)
	for c in (0, 4, 8):
		l3.setColumnStretch(c, 0)

	layout.addWidget(gb_cover)

	# 字幕 / 书库 / Coser
	gb_more1 = QGroupBox("字幕 / 书库 / Coser")
	gb_more1.setStyleSheet(ModernStyles.get_group_style(s))
	l4 = QGridLayout(gb_more1)

	self.sub_video_root = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.sub_video_root)
	self.sub_root = QLineEdit(SETTINGS["SUBTITLE_MATCH_SOURCE_DIR"]); conf_lineedit(self.sub_root)
	self.sub_prio = QLineEdit(",".join(SETTINGS.get("SUBTITLE_PRIORITY_DIRS", []))); conf_lineedit(self.sub_prio)
	btn_sub = QPushButton("字幕匹配复制"); conf_button(btn_sub, primary=True); btn_sub.clicked.connect(self.action_match_subs)

	self.srt_root = QLineEdit(SETTINGS["SRT_RENAME_DIR"]); conf_lineedit(self.srt_root)
	btn_srt = QPushButton("DMM字幕重命名"); conf_button(btn_srt); btn_srt.clicked.connect(self.action_rename_srt)

	self.book_src = QLineEdit(SETTINGS["BOOK_SOURCE_DIR"]); conf_lineedit(self.book_src)
	self.book_dst = QLineEdit(next(iter(SETTINGS["BOOK_PRESET_TARGETS"].values()))); conf_lineedit(self.book_dst)
	btn_book = QPushButton("书库整理"); conf_button(btn_book); btn_book.clicked.connect(self.action_books)

	self.coser_root = QLineEdit(SETTINGS["COSER_SOURCE_DIR"]); conf_lineedit(self.coser_root)
	btn_coser2 = QPushButton("Coser二级整理"); conf_button(btn_coser2); btn_coser2.clicked.connect(self.action_coser2)
	btn_coserA = QPushButton("Coser首字母"); conf_button(btn_coserA); btn_coserA.clicked.connect(self.action_coserA)

	r = 0
	l4.addWidget(QLabel("视频根:"), r,0); l4.addWidget(self.sub_video_root, r,1)
	l4.addWidget(QLabel("字幕根:"), r,2); l4.addWidget(self.sub_root, r,3)
	l4.addWidget(btn_sub, r,4); r+=1

	l4.addWidget(QLabel("字幕优先(逗号分隔):"), r,0); l4.addWidget(self.sub_prio, r,1,1,3); r+=1
	l4.addWidget(QLabel("SRT根:"), r,0); l4.addWidget(self.srt_root, r,1); l4.addWidget(btn_srt, r,2); r+=1

	l4.addWidget(QLabel("书源:"), r,0); l4.addWidget(self.book_src, r,1)
	l4.addWidget(QLabel("目标:"), r,2); l4.addWidget(self.book_dst, r,3)
	l4.addWidget(btn_book, r,4); r+=1

	l4.addWidget(QLabel("Coser根:"), r,0); l4.addWidget(self.coser_root, r,1)
	l4.addWidget(btn_coser2, r,2); l4.addWidget(btn_coserA, r,3)

	for c in (1, 3):
		l4.setColumnStretch(c, 2)
	for c in (0, 2, 4):
		l4.setColumnStretch(c, 0)

	layout.addWidget(gb_more1)

	# 视频 / 重命名 / NFO / Poster / 下载
	gb_more2 = QGroupBox("视频 / 重命名 / NFO / Poster / 下载")
	gb_more2.setStyleSheet(ModernStyles.get_group_style(s))
	l5 = QGridLayout(gb_more2)

	self.vid_rename_dir = QLineEdit(SETTINGS["VIDEO_RENAME_DIR"]); conf_lineedit(self.vid_rename_dir)
	btn_vid_rename = QPushButton("视频批量重命名(-4K)"); conf_button(btn_vid_rename); btn_vid_rename.clicked.connect(self.action_video_rename)

	self.folder_mark_dir = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.folder_mark_dir)
	btn_markC  = QPushButton("文件夹标记 -C"); conf_button(btn_markC); btn_markC.clicked.connect(self.action_folder_mark_C)
	btn_mark4K = QPushButton("文件夹标记 -4K(含内部)"); conf_button(btn_mark4K); btn_mark4K.clicked.connect(self.action_folder_mark_4k)

	self.nfo_src = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.nfo_src)
	self.nfo_dst = QLineEdit(SETTINGS["DEST_NFO_SORTED"]); conf_lineedit(self.nfo_dst)
	btn_nfo = QPushButton("NFO厂商整理"); conf_button(btn_nfo); btn_nfo.clicked.connect(self.action_nfo)

	self.poster_tpl = QLineEdit(SETTINGS["VIDEO_SOURCE_DIR"]); conf_lineedit(self.poster_tpl)
	self.poster_src = QLineEdit(SETTINGS["IMAGE_SOURCE_DIR"]); conf_lineedit(self.poster_src)
	btn_poster_match = QPushButton("Poster匹配替换"); conf_button(btn_poster_match); btn_poster_match.clicked.connect(self.action_poster_match)

	self.dl_url = QLineEdit(SETTINGS["DOWNLOAD_URL_TEMPLATE"]); conf_lineedit(self.dl_url)
	self.dl_save = QLineEdit(SETTINGS["DOWNLOAD_SAVE_DIR"]); conf_lineedit(self.dl_save)
	self.dl_range = QLineEdit("1-1000"); conf_lineedit(self.dl_range)
	btn_dl = QPushButton("序列下载"); conf_button(btn_dl, primary=True); btn_dl.clicked.connect(self.action_seq_download)

	r = 0
	l5.addWidget(QLabel("重命名目录:"), r,0); l5.addWidget(self.vid_rename_dir, r,1,1,3); l5.addWidget(btn_vid_rename, r,4); r+=1

	l5.addWidget(QLabel("文件夹标记目录:"), r,0); l5.addWidget(self.folder_mark_dir, r,1,1,2)
	l5.addWidget(btn_markC, r,3); l5.addWidget(btn_mark4K, r,4); r+=1

	l5.addWidget(QLabel("NFO源:"), r,0); l5.addWidget(self.nfo_src, r,1)
	l5.addWidget(QLabel("目标:"), r,2); l5.addWidget(self.nfo_dst, r,3); l5.addWidget(btn_nfo, r,4); r+=1

	l5.addWidget(QLabel("Poster模板根:"), r,0); l5.addWidget(self.poster_tpl, r,1)
	l5.addWidget(QLabel("图片源:"), r,2); l5.addWidget(self.poster_src, r,3); l5.addWidget(btn_poster_match, r,4); r+=1

	l5.addWidget(QLabel("URL模板:"), r,0); l5.addWidget(self.dl_url, r,1,1,2)
	l5.addWidget(QLabel("保存至:"), r,3); l5.addWidget(self.dl_save, r,4); r+=1

	l5.addWidget(QLabel("范围(起-止):"), r,0); l5.addWidget(self.dl_range, r,1); l5.addWidget(btn_dl, r,4)

	# 列伸展：输入列扩展
	l5.setColumnStretch(1, 2); l5.setColumnStretch(3, 2)
	for c in (0, 2, 4):
		l5.setColumnStretch(c, 0)

	layout.addWidget(gb_more2)
	layout.addStretch()

	scroll.setWidget(container)
	return scroll

	def apply_modern_style(self):
		self.setStyleSheet(ModernStyles.get_main_style(self.scale))

	# 基础事件
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
		if not source_dir: return
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
		source_dir = self.source_path.text(); target_dir = self.target_path.text()
		if not source_dir or not target_dir:
			QMessageBox.warning(self, "警告", "请选择源文件夹和目标文件夹！"); return
		if not os.path.exists(source_dir):
			QMessageBox.warning(self, "警告", "源文件夹不存在！"); return
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
		self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True)
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)

	def stop_organizing(self):
		if self.worker:
			self.worker.stop(); self.worker.wait()
		self.organizing_finished()

	def organizing_finished(self):
		self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)
		self.progress_bar.setVisible(False); self.statusBar().showMessage("就绪")

	def show_error(self, error_msg):
		QMessageBox.critical(self, "错误", error_msg)
		self.organizing_finished()

	# 工具套件动作
	def action_export_posters(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.export_posters_for_enhance(Path(self.topaz_src.text()), Path(self.topaz_work.text()), open_topaz=True)
		QMessageBox.information(self, "完成", f"已导出 {n} 个 Poster")

	def action_import_posters(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.import_enhanced_posters(Path(self.topaz_work.text()))
		QMessageBox.information(self, "完成", f"已导回 {n} 个 Poster")

	def action_extract_ed2k(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.extract_ed2k(Path(self.ed2k_base.text()), Path(self.ed2k_out.text()), auto_delete_txt=self.ed2k_delete.isChecked())
		QMessageBox.information(self, "完成", f"提取 {n} 条链接")

	def action_replace_covers(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.replace_covers_by_size(Path(self.cover_repo.text()), Path(self.cover_target.text()))
		QMessageBox.information(self, "完成", f"替换 {n} 个封面")

	def action_match_subs(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		prio = [x.strip() for x in self.sub_prio.text().split(',') if x.strip()]
		n = self.tools.match_and_copy_subtitles(Path(self.sub_video_root.text()), Path(self.sub_root.text()), prio)
		QMessageBox.information(self, "完成", f"复制 {n} 个字幕")

	def action_rename_srt(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.rename_srt_cid_to_bangou(Path(self.srt_root.text()))
		QMessageBox.information(self, "完成", f"重命名 {n} 个字幕")

	def action_books(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.organize_books(Path(self.book_src.text()), Path(self.book_dst.text()))
		QMessageBox.information(self, "完成", f"整理 {n} 个文件")

	def action_coser2(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.coser_group_level2(Path(self.coser_root.text()))
		QMessageBox.information(self, "完成", f"移动 {n} 个文件夹")

	def action_coserA(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.coser_group_by_letter(Path(self.coser_root.text()))
		QMessageBox.information(self, "完成", f"归档 {n} 个文件夹")

	def action_video_rename(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.video_batch_rename_files(Path(self.vid_rename_dir.text()), suffix="-4K")
		QMessageBox.information(self, "完成", f"重命名 {n} 个视频")

	def action_folder_mark_C(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.folder_and_files_rename(Path(self.folder_mark_dir.text()), mode='C')
		QMessageBox.information(self, "完成", f"处理 {n} 个文件夹")

	def action_folder_mark_4k(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.folder_and_files_rename(Path(self.folder_mark_dir.text()), mode='4K')
		QMessageBox.information(self, "完成", f"处理 {n} 个文件夹")

	def action_nfo(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.nfo_organize_by_maker(Path(self.nfo_src.text()), Path(self.nfo_dst.text()))
		QMessageBox.information(self, "完成", f"移动 {n} 个文件夹")

	def action_poster_match(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		n = self.tools.poster_replace_from_source(Path(self.poster_tpl.text()), Path(self.poster_src.text()))
		QMessageBox.information(self, "完成", f"替换 {n} 个Poster")

	def action_seq_download(self):
		self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
		try:
			start, end = [int(x) for x in self.dl_range.text().split('-',1)]
		except Exception:
			QMessageBox.warning(self, "错误", "范围格式应为 起-止，例如 1-1000"); return
		ok, fail = self.tools.sequence_download(self.dl_url.text(), Path(self.dl_save.text()), start, end)
		QMessageBox.information(self, "完成", f"成功 {ok} 失败 {fail}")
