# plex_renamer/core.py
from pathlib import Path
import re

VIDEO_EXT = {'.mp4', '.mkv', '.avi', '.mov'}


def clean_for_title(s: str) -> str:
    s = re.sub(r'(?i)(?:season|s)[ _]?\d+', '', s)
    s = re.sub(r'[._\[\]\(\){}-]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def parse_season_number(folder_name: str) -> int:
    """Попытка достать номер сезона из имени папки"""
    m = re.search(r'(?i)(?:season|s)[ _]?(\d+)', folder_name)
    if m:
        return int(m.group(1))
    return 1


def parse_episode_number(filename: str) -> int:
    """Попытка достать номер эпизода из имени файла"""
    m = re.search(r'(\d{1,3})', filename)
    return int(m.group(1)) if m else 1


def build_movie_name(file_path: Path) -> str:
    title = clean_for_title(file_path.stem)
    ext = file_path.suffix.lower()
    return f"{title}{ext}"


def build_episode_name(file_path: Path) -> str:
    season_number = parse_season_number(file_path.parent.name)
    episode_number = parse_episode_number(file_path.stem)
    show_name = clean_for_title(
        file_path.parent.name)  # берём имя шоу, родитель папки сезона
    ext = file_path.suffix.lower()
    return f"{show_name}_S{season_number:03}E{episode_number:02}{ext}"


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXT


def run_renamer(path, apply=False, callback=None, stop_flag=None):
    """
    path: str или Path до файла или каталога
    apply: bool, если True — переименовывать реально
    callback: callable(message:str=None, progress:int=None) для логов и прогресса
    stop_flag: threading.Event() для возможности остановки
    """
    path = Path(path)

    def log(msg=None, progress=None):
        if callback:
            callback(message=msg, progress=progress)
        else:
            if msg:
                print(msg)
            if progress is not None:
                print(f"Progress: {progress}%")

    if not path.exists():
        log("❌ Указанный путь не существует")
        return

    if path.is_file():
        # Фильм
        new_name = build_movie_name(path)
        target = path.parent / new_name
        log(f"Обработка фильма: {path.name}")
        if target != path:
            log(f"{path.name} -> {new_name}", progress=100)
            if apply:
                path.rename(target)
                log("Переименовано")
            else:
                log("Dry-run")
        else:
            log(f"{path.name} уже в правильном формате", progress=100)

    elif path.is_dir():
        # Сериал
        files = sorted([f for f in path.iterdir() if is_video_file(f)])
        total = len(files)
        if not files:
            log("Нет видеофайлов для обработки")
            return

        for idx, f in enumerate(files, start=1):
            if stop_flag and stop_flag.is_set():
                log("⏹ Работа остановлена пользователем")
                break

            new_name = build_episode_name(f)
            target = f.parent / new_name
            progress = int(idx / total * 100)

            if target != f:
                log(f"{f.name} -> {new_name}", progress=progress)
                if apply:
                    f.rename(target)
                    log("Переименовано")
                else:
                    log("Dry-run")
            else:
                log(f"{f.name} уже в правильном формате", progress=progress)
