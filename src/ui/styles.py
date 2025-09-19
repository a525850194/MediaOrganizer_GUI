#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class ModernStyles:
	@staticmethod
	def px(v, s): return f"{int(v*s)}px"

	@classmethod
	def get_main_style(cls, s=1.0):
		return f"""
			QMainWindow {{
				background-color: #f8f9fa;
			}}
			QGroupBox {{
				font-weight: bold;
				font-size: {cls.px(14, s)};
				color: #2c3e50;
				margin-top: {cls.px(10, s)};
			}}
			QGroupBox::title {{
				left: {cls.px(10, s)};
				padding: 0 {cls.px(10, s)} 0 {cls.px(10, s)};
			}}
		"""

	@classmethod
	def get_title_style(cls, s=1.0):
		return f"""
			QLabel {{
				padding: {cls.px(20, s)};
				background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
					stop:0 #3498db, stop:1 #2980b9);
				border-radius: {cls.px(15, s)};
				color: white;
				margin-bottom: {cls.px(10, s)};
			}}
		"""

	@classmethod
	def get_tab_style(cls, s=1.0):
		return f"""
			QTabWidget::pane {{
				border: {cls.px(2, s)} solid #bdc3c7;
				border-radius: {cls.px(10, s)};
				background-color: #ecf0f1;
			}}
			QTabBar::tab {{
				background-color: #95a5a6;
				color: white;
				padding: {cls.px(10, s)} {cls.px(20, s)};
				margin-right: {cls.px(2, s)};
				border-top-left-radius: {cls.px(8, s)};
				border-top-right-radius: {cls.px(8, s)};
			}}
			QTabBar::tab:selected {{ background-color: #3498db; }}
			QTabBar::tab:hover {{ background-color: #2980b9; }}
		"""

	@classmethod
	def get_group_style(cls, s=1.0):
		return f"""
			QGroupBox {{
				border: {cls.px(2, s)} solid #bdc3c7;
				border-radius: {cls.px(10, s)};
				margin-top: {cls.px(10, s)};
				padding-top: {cls.px(10, s)};
				background-color: white;
			}}
			QGroupBox::title {{
				left: {cls.px(10, s)};
				padding: 0 {cls.px(10, s)} 0 {cls.px(10, s)};
				color: #2c3e50;
				font-weight: bold;
			}}
		"""

	@classmethod
	def get_input_style(cls, s=1.0):
		return f"""
			QLineEdit, QComboBox {{
				border: {cls.px(2, s)} solid #bdc3c7;
				border-radius: {cls.px(8, s)};
				padding: {cls.px(8, s)} {cls.px(12, s)};
				background-color: white;
				font-size: {cls.px(12, s)};
				min-height: {cls.px(32, s)};
			}}
			QLineEdit:focus, QComboBox:focus {{ border-color: #3498db; }}
		"""

	@classmethod
	def get_button_style(cls, s=1.0, bg="#95a5a6", bg_h="#7f8c8d", bg_p="#6c7b7d"):
		return f"""
			QPushButton {{
				background-color: {bg};
				color: white;
				border: none;
				padding: {cls.px(10, s)} {cls.px(20, s)};
				border-radius: {cls.px(8, s)};
				font-weight: bold;
				font-size: {cls.px(12, s)};
				min-height: {cls.px(36, s)};
			}}
			QPushButton:hover {{ background-color: {bg_h}; }}
			QPushButton:pressed {{ background-color: {bg_p}; }}
			QPushButton:disabled {{ background-color: #bdc3c7; }}
		"""

	@classmethod
	def get_primary_button_style(cls, s=1.0):
		return cls.get_button_style(s, "#27ae60", "#229954", "#1e8449")

	@classmethod
	def get_danger_button_style(cls, s=1.0):
		return cls.get_button_style(s, "#e74c3c", "#c0392b", "#a93226")

	@classmethod
	def get_list_style(cls, s=1.0):
		return f"""
			QListWidget {{
				background-color: white;
				border: {cls.px(2, s)} solid #bdc3c7;
				border-radius: {cls.px(10, s)};
				padding: {cls.px(10, s)};
				font-size: {cls.px(12, s)};
			}}
			QListWidget::item {{
				padding: {cls.px(8, s)};
				border-bottom: {cls.px(1, s)} solid #ecf0f1;
			}}
			QListWidget::item:selected {{ background-color: #3498db; color: white; }}
			QListWidget::item:hover {{ background-color: #ecf0f1; }}
		"""

	@classmethod
	def get_log_style(cls, s=1.0):
		return f"""
			QTextEdit {{
				background-color: #2c3e50;
				color: #ecf0f1;
				border: {cls.px(1, s)} solid #34495e;
				border-radius: {cls.px(5, s)};
				padding: {cls.px(10, s)};
				font-family: 'Consolas', monospace;
				min-height: {cls.px(150, s)};
			}}
		"""
