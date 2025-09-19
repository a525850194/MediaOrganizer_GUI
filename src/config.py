# src/config.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

SETTINGS = {
	"TOPAZ_PHOTO_AI_PATH": r"C:\Program Files\Topaz Labs LLC\Topaz Photo AI\Topaz Photo AI.exe",
	"BANDIZIP_PATH": r"bandizip.exe",

	"LOG_DIR_PATH": r"C:\Users\a5258\Downloads\Compressed\工具\py脚本\整合\logs",

	"VIDEO_SOURCE_DIR": r"E:\cloud\CloudDrive\115\Mdc\JAV_output",
	"VIDEO_RENAME_DIR": r"E:\cloud\CloudDrive\115\x1080\增强破解\【1】",
	"COVER_SOURCE_DIR": r"E:\cloud\CloudDrive\115\x1080\图片\封面",

	"DEST_CENSORED": r"E:\cloud\CloudDrive\115\【Media】\【有码系列】",
	"DEST_SUBTITLED_SERIES": r"E:\cloud\CloudDrive\115\【Media】\【字幕系列】",
	"DEST_AMATEUR": r"E:\cloud\CloudDrive\115\【Media】\【素人系列】",
	"DEST_AI_4K": r"E:\cloud\CloudDrive\115\【Media】\【4K-AI】",
	"DEST_4K_SERIES": r"E:\cloud\CloudDrive\115\【Media】\【4K系列】",
	"DEST_NFO_SORTED": r"E:\cloud\CloudDrive\115\【Media】\【4K系列】",

	"COSER_SOURCE_DIR": r"G:\我的云端硬盘\【Immich】\【PTer】\【Coser写真】",

	"SUBTITLE_MATCH_SOURCE_DIR": r"C:\Users\a5258\Downloads\Compressed\X1080\字幕",
	"SUBTITLE_PRIORITY_DIRS": ['X1080字幕', '34000字幕'],
	"SRT_RENAME_DIR": r"C:\Users\a5258\Downloads\Compressed\X1080\字幕",

	"BOOK_SOURCE_DIR": r"G:\我的云端硬盘\2",
	"BOOK_PRESET_TARGETS": {
		"1": r"G:\我的云端硬盘\【Kavita】\【books】\【鬼鬼制作】",
		"2": r"G:\我的云端硬盘\【Kavita】\【books】\【怪哥制作】",
		"3": r"G:\我的云端硬盘\【Kavita】\【books】\【多位大佬制作】"
	},

	"DOWNLOAD_SAVE_DIR": r"C:\Users\a5258\Downloads\Compressed\图片",
	"IMAGE_SOURCE_DIR": r"C:\Users\a5258\Downloads\Compressed\图片",
	"DOWNLOAD_URL_TEMPLATE": "https://image.mgstage.com/images/magictabloid/300ntk/{num}/pf_e_300ntk-{num}.jpg",

	"ED2K_SOURCE_DIR": r"C:\Users\a5258\Downloads\Compressed\X1080",
	"ED2K_OUTPUT_DIR": r"C:\Users\a5258\Downloads",
	"ED2K_TARGET_HEADER": "115視頻格式離綫下載地址：",

	"LOG_FILE_NAME": "整理日志.txt",
	"VIDEO_EXTENSIONS": ('.mkv', '.mp4', '.avi', '.ts', '.mov', '.webm'),
	"SUBTITLE_EXTENSIONS": ('.srt', '.ass', '.ssa', '.vtt'),
	"SUBTITLE_EXCLUDE_KEYWORDS": ['trailer'],
	"IMAGE_EXTENSIONS": ('.jpg', '.jpeg', '.png', '.webp'),
}
