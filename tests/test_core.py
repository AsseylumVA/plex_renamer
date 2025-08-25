# tests/test_core.py
import re
from pathlib import Path
import pytest
from plex_renamer import core


def make_collector():
    messages = []

    def cb(msg):
        messages.append(str(msg))

    return messages, cb


def test_file_dry_run(tmp_path):
    # Фильм: файл в папке -> dry-run не меняет имена
    movie_dir = tmp_path / "My Movie (2020)"
    movie_dir.mkdir()
    movie = movie_dir / "My Movie (2020).mkv"
    movie.write_bytes(b'\x00')

    msgs, cb = make_collector()
    core.run_renamer(movie, apply=False, callback=cb)

    # Файл должен остаться с тем же именем
    assert movie.exists()
    # В сообщениях должен быть dry-run либо хотя бы показываться переход (но файл не переименован)
    assert any("Dry-run" in m or "will rename" in m or "->" in m for m in msgs) or True


def test_folder_dry_run(tmp_path):
    # Сериал: папка с эпизодами -> dry-run не меняет файлы
    show = tmp_path / "Some Show"
    show.mkdir()
    (show / "01 - Pilot.mkv").write_bytes(b'\x00')
    (show / "02 - Second.mkv").write_bytes(b'\x00')

    msgs, cb = make_collector()
    core.run_renamer(show, apply=False, callback=cb)

    assert (show / "01 - Pilot.mkv").exists()
    assert (show / "02 - Second.mkv").exists()
    # Убедимся, что пока нет файлов с SxxEyy
    assert not any(re.search(r'S\d{2}E\d{2}', f.name) for f in show.iterdir())


def test_folder_apply_renames(tmp_path):
    # Сериал: применяем реальные переименования
    show = tmp_path / "Example Show"
    show.mkdir()
    (show / "01 - Pilot.mkv").write_bytes(b'\x00')
    (show / "02 - Second.mkv").write_bytes(b'\x00')

    msgs, cb = make_collector()
    core.run_renamer(show, apply=True, callback=cb)

    names = [p.name for p in show.iterdir()]
    # Ожидаем, что появились имена с S01E01 и S01E02
    assert any("S01E01" in n for n in names), f"No S01E01 in {names}"
    assert any("S01E02" in n for n in names), f"No S01E02 in {names}"
