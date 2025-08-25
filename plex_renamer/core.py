from pathlib import Path
import re

VIDEO_EXT = {'.mp4', '.mkv', '.avi', '.mov'}

def clean_for_title(s: str) -> str:
    s = re.sub(r'[._]+', ' ', s)
    s = re.sub(r'[\[\]\(\){}_]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip(' -._')

def parse_episode_number(filename: str) -> int:
    """Попытка достать номер эпизода из имени файла"""
    m = re.match(r'^\s*(\d{1,3})', filename)
    return int(m.group(1)) if m else 1

def build_movie_name(file_path: Path) -> str:
    title = clean_for_title(file_path.parent.name)
    ext = file_path.suffix
    return f"{title}{ext}"

def build_episode_name(file_path: Path, episode_number: int) -> str:
    show_name = clean_for_title(file_path.parent.name)
    season_number = 1  # упрощаем: сезон 1
    ep_title = clean_for_title(file_path.stem)
    ext = file_path.suffix
    return f"{show_name} - S{season_number:02}E{episode_number:02} - {ep_title}{ext}"

def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXT

def run_renamer(path, apply=False, callback=None):
    """
    path: str или Path до файла или каталога
    apply: bool, если True — переименовывать реально
    callback: callable, callback(str) для логов
    """
    path = Path(path)
    def log(msg):
        if callback:
            callback(str(msg))
        else:
            print(msg)

    if path.is_file():
        # Фильм
        new_name = build_movie_name(path)
        target = path.parent / new_name
        if target != path:
            log(f"{path} -> {target}")
            if apply:
                path.rename(target)
                log("Переименовано")
            else:
                log("Dry-run")
        else:
            log(f"{path} уже в правильном формате")
    elif path.is_dir():
        # Сериал — обрабатываем все видео внутри каталога
        files = sorted([f for f in path.iterdir() if is_video_file(f)])
        if not files:
            log("Нет видеофайлов для обработки")
            return
        for idx, f in enumerate(files, start=1):
            new_name = build_episode_name(f, idx)
            target = f.parent / new_name
            if target != f:
                log(f"{f} -> {target}")
                if apply:
                    f.rename(target)
                    log("Переименовано")
                else:
                    log("Dry-run")
            else:
                log(f"{f} уже в правильном формате")
    else:
        log("Указанный путь не существует")
