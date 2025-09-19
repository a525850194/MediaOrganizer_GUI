#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, csv, shutil, subprocess, datetime, time
from pathlib import Path
from typing import Callable, List, Dict
from .config import SETTINGS

C_GREEN = ""; C_RED = ""; C_YELLOW = ""; C_RESET = ""; C_CYAN = ""; C_MAGENTA = ""; C_GRAY = ""

def _ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)
def _fmt_size(n: int) -> str:
	if n < 1024: return f"{n} B"
	if n < 1024**2: return f"{n/1024:.2f} KB"
	if n < 1024**3: return f"{n/1024**2:.2f} MB"
	return f"{n/1024**3:.2f} GB"

class Logger:
	def __init__(self, log_dir: Path, filename: str, sink: Callable[[str], None] = lambda s: None):
		self.log_dir, self.filename, self.sink = Path(log_dir), filename, sink
		_ensure_dir(self.log_dir)
		self.path = self.log_dir / filename
		if not self.path.exists():
			self.path.write_text("--- 全局操作日志 ---\n", encoding="utf-8")

	def write(self, msg: str):
		ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.sink(msg)
		with self.path.open("a", encoding="utf-8") as f:
			f.write(f"[{ts}] {msg}\n")

class MediaToolkit:
	def __init__(self, notify: Callable[[str], None] = lambda s: None, progress: Callable[[int], None] = lambda v: None):
		self.notify, self.progress = notify, progress
		self.logger = Logger(Path(SETTINGS["LOG_DIR_PATH"]), SETTINGS["LOG_FILE_NAME"], sink=self.notify)

	# ---------- ED2K: 自动解压 + 提取 ----------
	def _preprocess_archives(self, directory: Path):
		bz = SETTINGS.get("BANDIZIP_PATH")
		if not bz or not shutil.which(bz):
			self.notify("找不到 Bandizip，可在设置中配置 BANDIZIP_PATH"); return
		pwd = None
		pwd_file = directory / "解壓密碼.txt"
		if pwd_file.exists():
			try:
				pwd = pwd_file.read_text(encoding="utf-8", errors="ignore").strip().splitlines()[0]
				self.notify("发现密码文件，将尝试使用")
			except Exception: pass

		archives = [p for p in directory.iterdir() if p.suffix.lower() in (".rar",".zip",".7z")]
		for i, arc in enumerate(archives, 1):
			cmd = [bz, "x", f"-o:{str(directory)}", "-y"]
			if pwd: cmd.append(f"-p:{pwd}")
			cmd.append(str(arc))
			try:
				startupinfo=None
				if os.name=="nt":
					startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="cp950", errors="ignore", startupinfo=startupinfo)
				self.notify(f"解压成功: {arc.name}")
				try: arc.unlink()
				except Exception: pass
			except subprocess.CalledProcessError as e:
				self.notify(f"解压失败: {arc.name} ({e.stderr.strip()[:200]})")
			self.progress(int(i*100/len(archives)) if archives else 0)
		if pwd_file.exists():
			try: pwd_file.unlink()
			except Exception: pass

	def extract_ed2k(self, base_dir: Path, output_dir: Path, auto_delete_txt: bool = True) -> int:
		self.notify("开始 ED2K 提取")
		_ensure_dir(output_dir)
		ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		out_file = output_dir / f"ed2k_links_{ts}.txt"

		total_links = 0
		for folder in [p for p in Path(base_dir).rglob("*") if p.is_dir()] + [Path(base_dir)]:
			self._preprocess_archives(folder)

			extracted, deletions = [], []
			header = SETTINGS["ED2K_TARGET_HEADER"]
			for txt in folder.rglob("*.txt"):
				in_block, found = False, False
				try:
					for line in txt.read_text(encoding="utf-8", errors="ignore").splitlines():
						line = line.strip()
						if header in line: in_block=True; continue
						if in_block:
							if not line or line.endswith((':','：')): in_block=False; continue
							if line.startswith("ed2k://"):
								extracted.append(line); found=True
				except Exception: pass
				if found: deletions.append(txt)

			if extracted:
				with out_file.open("a", encoding="utf-8") as f:
					for link in extracted: f.write(link+"\n")
				total_links += len(extracted)
				if auto_delete_txt:
					for t in deletions:
						try: t.unlink()
						except Exception: pass

		self.logger.write(f"[ED2K] 共提取 {total_links} 条 -> {out_file}")
		self.notify(f"完成，输出: {out_file}")
		return total_links

	# ---------- Poster 导出/导回（Topaz） ----------
	def export_posters_for_enhance(self, source_dir: Path, work_dir: Path, open_topaz: bool = True) -> int:
		mapping_csv = Path(SETTINGS["LOG_DIR_PATH"]) / "poster_mapping.csv"
		_ensure_dir(work_dir); _ensure_dir(mapping_csv.parent)

		items: List[Dict] = []
		for p in Path(source_dir).rglob("*"):
			if p.is_file() and ("poster" in p.name.lower()) and p.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]:
				try: size = p.stat().st_size
				except Exception: continue
				items.append({"path": p, "name": p.name, "size": size, "parent": p.parent.name})
		items.sort(key=lambda x: x["size"])

		with mapping_csv.open("w", newline="", encoding="utf-8") as f:
			w = csv.writer(f); w.writerow(["filename","original_path"])
			for i, it in enumerate(items, 1):
				shutil.copy2(str(it["path"]), str(Path(work_dir)/it["name"]))
				w.writerow([it["name"], str(it["path"])])
				self.progress(int(i*100/len(items)) if items else 0)

		self.logger.write(f"[Topaz导出] {len(items)} 个 -> {work_dir} / 映射: {mapping_csv}")
		if open_topaz:
			topaz = SETTINGS.get("TOPAZ_PHOTO_AI_PATH")
			if topaz and Path(topaz).exists():
				try:
					subprocess.Popen([topaz, str(work_dir)])
					self.notify("Topaz Photo AI 已启动")
				except Exception as e:
					self.notify(f"启动 Topaz 失败: {e}")
		return len(items)

	def import_enhanced_posters(self, work_dir: Path) -> int:
		mapping_csv = Path(SETTINGS["LOG_DIR_PATH"]) / "poster_mapping.csv"
		if not mapping_csv.exists():
			self.notify("找不到 poster_mapping.csv，请先执行导出"); return 0
		rows = list(csv.reader(mapping_csv.open("r", encoding="utf-8")))
		if rows and rows[0] and rows[0][0]=="filename": rows = rows[1:]
		count = 0
		for i, (fname, orig) in enumerate(rows, 1):
			src = Path(work_dir)/fname
			dst = Path(orig)
			if src.exists():
				try:
					shutil.copy2(str(src), str(dst))
					count += 1
				except Exception as e:
					self.notify(f"导回失败 {fname}: {e}")
			self.progress(int(i*100/len(rows)) if rows else 0)
		self.logger.write(f"[Topaz导回] 成功 {count}/{len(rows)}")
		return count

	# ---------- 封面替换（对比大小） ----------
	def replace_covers_by_size(self, cover_repo: Path, target_root: Path) -> int:
		# 建索引：同番号取更大尺寸
		def id_from_name(name: str):
			m = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)', name, re.IGNORECASE)
			return m.group(1).upper() if m else None

		index: Dict[str, Dict] = {}
		for p in Path(cover_repo).rglob("*"):
			if p.is_file() and p.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]:
				bid = id_from_name(p.name)
				if not bid: continue
				sz = p.stat().st_size
				if bid not in index or sz > index[bid]["size"]:
					index[bid] = {"path": p, "size": sz}

		replace_list: List[Dict] = []
		for img in Path(target_root).rglob("*"):
			if not (img.is_file() and img.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]): continue
			name = img.stem.lower()
			if not (name.endswith("-fanart") or name.endswith("-thumb")): continue
			bid = id_from_name(img.name)
			if not bid or bid not in index: continue
			try:
				target_size = img.stat().st_size
			except Exception:
				continue
			if index[bid]["size"] > target_size:
				replace_list.append({"src": index[bid]["path"], "dst": img})

		for i, it in enumerate(replace_list, 1):
			try:
				if it["dst"].exists(): it["dst"].unlink()
				shutil.copy2(str(it["src"]), str(it["dst"]))
			except Exception as e:
				self.notify(f"替换失败 {it['dst'].name}: {e}")
			self.progress(int(i*100/len(replace_list)) if replace_list else 0)

		self.logger.write(f"[封面替换] 成功 {len(replace_list)}")
		return len(replace_list)
