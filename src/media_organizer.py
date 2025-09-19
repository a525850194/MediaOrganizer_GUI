# src/media_organizer.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, csv, shutil, subprocess, datetime, time
from pathlib import Path
from typing import Callable, List, Dict, Tuple
from config import SETTINGS

def _ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

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

	# ------------ 内部：Bandizip 解压 ------------
	def _preprocess_archives(self, directory: Path):
		bz = SETTINGS.get("BANDIZIP_PATH")
		if not bz or not shutil.which(bz):
			self.notify("找不到 Bandizip，请在设置中配置 BANDIZIP_PATH")
			return
		pwd = None
		pwd_file = directory / "解壓密碼.txt"
		if pwd_file.exists():
			try:
				pwd = pwd_file.read_text(encoding="utf-8", errors="ignore").strip().splitlines()[0]
				self.notify("发现密码文件，将尝试使用")
			except Exception:
				pass
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
				self.notify(f"解压失败: {arc.name} ({(e.stderr or '')[:200]})")
			self.progress(int(i*100/len(archives)) if archives else 0)
		if pwd_file.exists():
			try: pwd_file.unlink()
			except Exception: pass

	# ------------ ED2K 提取 ------------
	def extract_ed2k(self, base_dir: Path, output_dir: Path, auto_delete_txt: bool = True) -> int:
		self.notify("开始 ED2K 提取")
		_ensure_dir(output_dir)
		ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		out_file = output_dir / f"ed2k_links_{ts}.txt"
		total = 0
		for folder in [p for p in Path(base_dir).rglob("*") if p.is_dir()] + [Path(base_dir)]:
			self._preprocess_archives(folder)
			extracted, deletions = [], []
			header = SETTINGS["ED2K_TARGET_HEADER"]
			for txt in folder.rglob("*.txt"):
				in_block = False; found = False
				try:
					for line in txt.read_text(encoding="utf-8", errors="ignore").splitlines():
						line = line.strip()
						if header in line: in_block=True; continue
						if in_block:
							if not line or line.endswith((':','：')): in_block=False; continue
							if line.startswith("ed2k://"):
								extracted.append(line); found=True
				except Exception:
					pass
				if found: deletions.append(txt)
			if extracted:
				with out_file.open("a", encoding="utf-8") as f:
					for link in extracted: f.write(link+"\n")
				total += len(extracted)
				if auto_delete_txt:
					for t in deletions:
						try: t.unlink()
						except Exception: pass
		self.logger.write(f"[ED2K] 共提取 {total} 条 -> {out_file}")
		self.notify(f"完成，输出: {out_file}")
		return total

	# ------------ Topaz 导出/导回 ------------
	def export_posters_for_enhance(self, source_dir: Path, work_dir: Path, open_topaz: bool = True) -> int:
		mapping_csv = Path(SETTINGS["LOG_DIR_PATH"]) / "poster_mapping.csv"
		_ensure_dir(work_dir); _ensure_dir(mapping_csv.parent)
		items = []
		for p in Path(source_dir).rglob("*"):
			if p.is_file() and ("poster" in p.name.lower()) and p.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]:
				try: size = p.stat().st_size
				except Exception: continue
				items.append({"path": p, "name": p.name, "size": size})
		items.sort(key=lambda x: x["size"])
		with mapping_csv.open("w", newline="", encoding="utf-8") as f:
			w = csv.writer(f); w.writerow(["filename","original_path"])
			for i, it in enumerate(items, 1):
				shutil.copy2(str(it["path"]), str(Path(work_dir)/it["name"]))
				w.writerow([it["name"], str(it["path"])])
				self.progress(int(i*100/len(items)) if items else 0)
		self.logger.write(f"[Topaz导出] {len(items)} 个 -> {work_dir} / 映射: {mapping_csv}")
		topaz = SETTINGS.get("TOPAZ_PHOTO_AI_PATH")
		if open_topaz and topaz and Path(topaz).exists():
			try: subprocess.Popen([topaz, str(work_dir)]); self.notify("Topaz Photo AI 已启动")
			except Exception as e: self.notify(f"启动 Topaz 失败: {e}")
		return len(items)

	def import_enhanced_posters(self, work_dir: Path) -> int:
		mapping_csv = Path(SETTINGS["LOG_DIR_PATH"]) / "poster_mapping.csv"
		if not mapping_csv.exists():
			self.notify("找不到 poster_mapping.csv，请先执行导出"); return 0
		rows = list(csv.reader(mapping_csv.open("r", encoding="utf-8")))
		if rows and rows[0] and rows[0][0]=="filename": rows = rows[1:]
		count = 0
		for i, (fname, orig) in enumerate(rows, 1):
			src = Path(work_dir)/fname; dst = Path(orig)
			if src.exists():
				try: shutil.copy2(str(src), str(dst)); count += 1
				except Exception as e: self.notify(f"导回失败 {fname}: {e}")
			self.progress(int(i*100/len(rows)) if rows else 0)
		self.logger.write(f"[Topaz导回] 成功 {count}/{len(rows)}")
		return count

	# ------------ 封面替换（对比大小） ------------
	def replace_covers_by_size(self, cover_repo: Path, target_root: Path) -> int:
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
		replaces = []
		for img in Path(target_root).rglob("*"):
			if not (img.is_file() and img.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]): continue
			stem = img.stem.lower()
			if not (stem.endswith("-fanart") or stem.endswith("-thumb")): continue
			bid = id_from_name(img.name)
			if not bid or bid not in index: continue
			try: tsize = img.stat().st_size
			except Exception: continue
			if index[bid]["size"] > tsize:
				replaces.append({"src": index[bid]["path"], "dst": img})
		for i, it in enumerate(replaces, 1):
			try:
				if it["dst"].exists(): it["dst"].unlink()
				shutil.copy2(str(it["src"]), str(it["dst"]))
			except Exception as e:
				self.notify(f"替换失败 {it['dst'].name}: {e}")
			self.progress(int(i*100/len(replaces)) if replaces else 0)
		self.logger.write(f"[封面替换] 成功 {len(replaces)}")
		return len(replaces)

	# ------------ 字幕匹配复制 ------------
	def match_and_copy_subtitles(self, video_root: Path, subs_root: Path, priority_dirs: list, exts=('.srt','.ass','.ssa','.vtt')) -> int:
		def base_id(name: str):
			m = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)', name, re.IGNORECASE)
			return m.group(1).upper() if m else None
		video_map: Dict[str, List[Path]] = {}
		for p in video_root.rglob("*"):
			if p.is_file() and p.suffix.lower() in SETTINGS["VIDEO_EXTENSIONS"]:
				if any(x in p.name.lower() for x in [k.lower() for k in SETTINGS["SUBTITLE_EXCLUDE_KEYWORDS"]]): continue
				bid = base_id(p.name)
				if bid: video_map.setdefault(bid, []).append(p)

		search_paths = []
		for d in (priority_dirs or []):
			pp = subs_root / d
			if pp.is_dir(): search_paths.append(pp)
		if subs_root not in search_paths: search_paths.append(subs_root)

		def best_for_id(bid: str) -> List[Path]:
			for root in search_paths:
				cands = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts and base_id(p.name)==bid]
				if not cands: continue
				whole = [p for p in cands if p.stem.upper()==bid]
				if whole:
					ass = [p for p in whole if p.suffix.lower()=='.ass']
					return [ass[0]] if ass else [whole[0]]
				ass_parts = [p for p in cands if p.suffix.lower()=='.ass']
				if ass_parts: return sorted(ass_parts)
				srt_parts = [p for p in cands if p.suffix.lower()=='.srt']
				if srt_parts: return sorted(srt_parts)
			return []

		copied = 0
		for i, (bid, vids) in enumerate(video_map.items(), 1):
			sel = best_for_id(bid)
			for v in vids:
				base = v.with_suffix('')
				for sub in sel:
					newname = base.name
					if not any(newname.lower().endswith(t) for t in ['.chs','.sc','.zh','.cn','.simp']):
						dest = base.parent / (newname + '.chs' + sub.suffix)
					else:
						dest = base.parent / (newname + sub.suffix)
					if not dest.exists():
						shutil.copy2(str(sub), str(dest)); copied += 1
			self.progress(int(i*100/len(video_map)) if video_map else 0)
		self.logger.write(f"[字幕匹配] 复制 {copied} 个")
		return copied

	# ------------ DMM 字幕重命名 ------------
	def rename_srt_cid_to_bangou(self, root: Path) -> int:
		def conv(name: str):
			if not name.lower().endswith('.srt'): return None
			n = Path(name).stem
			ms = re.findall(r'([a-zA-Z]+)(\d+)', n)
			if not ms: return None
			label, num = ms[-1]
			if len(label) < 2: return None
			return f"{label.upper()}-{int(num):03d}.srt"
		renamed = 0
		all_srt = [p for p in root.rglob("*.srt")]
		for i, p in enumerate(all_srt, 1):
			new = conv(p.name)
			if new and new != p.name:
				dest = p.with_name(new)
				try: p.rename(dest); renamed += 1
				except Exception: pass
			self.progress(int(i*100/len(all_srt)) if all_srt else 0)
		self.logger.write(f"[字幕重命名] {renamed} 个")
		return renamed

	# ------------ 书库整理 ------------
	def organize_books(self, source_dir: Path, target_dir: Path, logic_type: str='1') -> int:
		def title_A(fn: str):
			name = Path(fn).stem
			i = name.rfind(']')
			if i != -1: name = name[:i+1]
			import re as _re
			book = _re.sub(r'\[[^\]]*\]|【[^】]*】', '', name).strip()
			return book or Path(fn).stem
		def title_B(fn: str):
			name = Path(fn).stem
			i = name.find('[')
			if i != -1: name = name[:i]
			import re as _re
			name = _re.sub(r'^[A-Z\d\-]+\s*', '', name)
			name = _re.sub(r'\s*\d+\.\d+\s*$', '', name)
			return name.strip() or Path(fn).stem

		files = [p for p in Path(source_dir).iterdir() if p.is_file()]
		moved = 0
		for i, f in enumerate(files, 1):
			base = title_A(f.name) if logic_type=='2' else title_B(f.name)
			dest_dir = Path(target_dir)/base
			_ensure_dir(dest_dir)
			dest = dest_dir / f.name
			if dest.exists():
				if f.stat().st_size == dest.stat().st_size:
					shutil.move(str(f), str(dest))
				else:
					exist = [x for x in dest_dir.iterdir() if x.is_file()]
					if len(exist) == 1:
						old = exist[0]
						old.rename(dest_dir / f"{base}-版本1{old.suffix}")
					new_ver = len(list(dest_dir.iterdir())) + 1
					shutil.move(str(f), str(dest_dir / f"{base}-版本{new_ver}{f.suffix}"))
			else:
				shutil.move(str(f), str(dest))
			moved += 1
			self.progress(int(i*100/len(files)) if files else 0)
		self.logger.write(f"[书库整理] {moved} 个")
		return moved

	# ------------ Coser 二级整理 ------------
	def coser_group_level2(self, root: Path) -> int:
		moved = 0
		for top in [p for p in Path(root).iterdir() if p.is_dir()]:
			for sub in [p for p in top.iterdir() if p.is_dir() and ' - ' in p.name]:
				name = sub.name.split(' - ', 1)[0].strip()
				dest_parent = Path(root) / name
				_ensure_dir(dest_parent)
				shutil.move(str(sub), str(dest_parent))
				moved += 1
		self.logger.write(f"[Coser二级] 移动 {moved} 个")
		return moved

	# ------------ Coser 按首字母 ------------
	def coser_group_by_letter(self, root: Path) -> int:
		try:
			from pypinyin import pinyin, Style
		except Exception:
			pinyin = None
		def first_letter(s: str) -> str:
			if not s: return '#'
			c = s[0]
			if 'a' <= c.lower() <= 'z': return c.upper()
			if pinyin:
				py = pinyin(c, style=Style.FIRST_LETTER)
				if py and py[0] and 'a' <= py[0][0].lower() <= 'z': return py[0][0].upper()
			return '#'
		moved = 0
		for folder in [p for p in Path(root).iterdir() if p.is_dir()]:
			if re.match(r'^【[A-Z0-9#]】$', folder.name): continue
			dest = Path(root) / f"【{first_letter(folder.name)}】"
			_ensure_dir(dest)
			shutil.move(str(folder), str(dest))
			moved += 1
		self.logger.write(f"[Coser首字母] 归档 {moved} 个")
		return moved

	# ------------ 视频批量重命名（文件） ------------
	def video_batch_rename_files(self, directory: Path, suffix="-4K") -> int:
		pat = re.compile(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)')
		ren = 0
		files = [p for p in Path(directory).iterdir() if p.is_file()]
		for i, f in enumerate(files, 1):
			m = pat.search(f.name.upper())
			if m:
				new = f"{m.group(1)}{suffix}{f.suffix}"
				if new != f.name:
					f.rename(f.with_name(new)); ren += 1
			self.progress(int(i*100/max(1,len(files))))
		self.logger.write(f"[视频重命名] {ren} 个")
		return ren

	# ------------ 文件夹命名 C/4K ------------
	def folder_and_files_rename(self, source_dir: Path, mode: str='C') -> int:
		suffix = f"-{mode.upper()}"
		changed = 0
		for folder in [p for p in Path(source_dir).iterdir() if p.is_dir()]:
			if folder.name.upper().endswith(('-C','-4K')): continue
			new_folder = folder.with_name(folder.name + suffix)
			folder.rename(new_folder); changed += 1
			if mode.upper() == '4K':
				for f in new_folder.iterdir():
					if f.is_file():
						base = f.stem
						if '-4K' in base: continue
						m = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)', base, re.IGNORECASE)
						if m: newbase = base.replace(m.group(1), f"{m.group(1)}-4K", 1)
						else: newbase = base + '-4K'
						f.rename(f.with_name(newbase + f.suffix))
		self.logger.write(f"[文件夹命名{mode}] {changed} 个")
		return changed

	# ------------ NFO 厂商整理 ------------
	def nfo_organize_by_maker(self, source_root: Path, dest_root: Path) -> int:
		import xml.etree.ElementTree as ET
		def maker_from_dir(d: Path):
			try:
				nfo = next(x for x in d.iterdir() if x.suffix.lower()=='.nfo')
				root = ET.parse(str(nfo)).getroot()
				for tag in ('maker','studio'):
					el = root.find(tag)
					if el is not None and el.text: 
						return re.sub(r'[\\/*?:"<>|]', '_', el.text.strip())
			except Exception:
				return None
		moved = 0
		for d, _, files in os.walk(source_root):
			p = Path(d)
			if not any(x.lower().endswith('.nfo') for x in files): continue
			maker = maker_from_dir(p)
			if not maker: continue
			folder_name = p.name
			key_m = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)', folder_name, re.IGNORECASE)
			dest_man = Path(dest_root)/f"【{maker}】"
			dest_parent = dest_man / f"【{key_m.group(1).split('-')[0]}】" if key_m else dest_man
			_ensure_dir(dest_parent)
			if not (dest_parent/folder_name).exists():
				shutil.move(str(p), str(dest_parent)); moved += 1
		self.logger.write(f"[NFO整理] 移动 {moved} 个")
		return moved

	# ------------ Poster 匹配替换 ------------
	def poster_replace_from_source(self, jav_output: Path, image_source: Path) -> int:
		def id_of(name: str):
			m = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)', name, re.IGNORECASE)
			return m.group(1).upper() if m else None
		src_list = [p for p in Path(image_source).iterdir() if p.is_file() and p.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]]
		replaced = 0
		for p in Path(jav_output).rglob("*"):
			if p.is_file() and 'poster' in p.name.lower() and p.suffix.lower() in SETTINGS["IMAGE_EXTENSIONS"]:
				bid = id_of(p.name); 
				if not bid: continue
				pat = re.compile(r'(?:^|[^a-zA-Z0-9])' + re.escape(bid) + r'(?:[^a-zA-Z0-9]|$)', re.IGNORECASE)
				src = next((s for s in src_list if pat.search(s.name)), None)
				if src:
					shutil.copy2(str(src), str(p)); replaced += 1
		self.logger.write(f"[Poster替换] {replaced} 个")
		return replaced

	# ------------ 序列下载 ------------
	def sequence_download(self, url_tmpl: str, save_dir: Path, start: int, end: int, padding: int=3, batch: int=50, pause: int=30) -> Tuple[int,int]:
		import requests
		_ensure_dir(save_dir)
		ok = fail = 0
		total = max(1, end-start+1)
		for i in range(start, end+1):
			num = f"{i:0{padding}d}"
			url = url_tmpl.format(num=num)
			dest = save_dir / url.split('/')[-1]
			try:
				r = requests.get(url, timeout=30, stream=True)
				if r.status_code == 200:
					with dest.open('wb') as f:
						for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
					ok += 1
				else:
					fail += 1
			except Exception:
				fail += 1
			if batch>0 and (i-start+1)%batch==0 and i<end:
				time.sleep(pause)
			self.progress(int((i-start+1)*100/total))
		self.logger.write(f"[序列下载] 成功 {ok} 失败 {fail}")
		return ok, fail
