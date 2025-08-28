from pathlib import Path
import tempfile
from plex_renamer import core


def test_clean_for_title_and_parse_season():
    assert core.clean_for_title("test s023 - s023") == "test"
    assert core.parse_season_number("Season01") == 1
    assert core.parse_season_number("season_2") == 2
    assert core.parse_season_number("S03") == 3
    assert core.parse_season_number("s 4") == 4
    assert core.parse_season_number("Show") == 1  # если нет сезона
    real_show_name = "Itai no wa Iya nano de Bougyoryokuni " \
                     "Kyokufuri Shitai to Omoimasu 2 " \
                     " - AniLibria.TV [WEBRip 1080p HEVC]"
    assert core.parse_season_number(real_show_name) == 2
    real_show_name = "Sono_Bisque_Doll_wa_Koi_wo_Suru_S01_2022"
    assert core.parse_season_number(real_show_name) == 1


def test_parse_episode_number():
    assert core.parse_episode_number("01 - title") == 1
    assert core.parse_episode_number("03title") == 3
    assert core.parse_episode_number("no_number") == 1
    real_episode_number1 = "Itai_no_wa_Iya_nano_de_Bougyoryoku"\
                          "_ni_Kyokufuri_Shitai_to_Omoimasu_2_[01]"\
                          "_[AniLibria_TV]_[WEBRip_1080p_HEVC]"
    assert core.parse_episode_number(real_episode_number1) == 1
    real_episode_number2 = "[Deadmau-RAWS] Sono.Bisque.Doll.wa.Koi."\
                           "wo.Suru.S01.2022.BDRip.1080p.x264.FLAC."\
                           "Deadmauvlad.Ep.04"
    assert core.parse_episode_number(real_episode_number2) == 4


def test_build_movie_name():
    path = Path("/tmp/Some.Movie.2023.MKV")
    expected = "Some Movie 2023.mkv"
    assert core.build_movie_name(path) == expected


def test_build_episode_name():
    folder = Path("/tmp/test season_2")
    file_path = folder / "03 - episode.mkv"
    expected = "test_S002E03.mkv"
    assert core.build_episode_name(file_path) == expected


def test_run_renamer_dry_run_movie():
    with tempfile.TemporaryDirectory() as tmpdir:
        f = Path(tmpdir) / "Movie.2023.mkv"
        f.touch()
        logs = []

        core.run_renamer(f, apply=False, callback=lambda message=None,
                                                         progress=None: logs.append(
            message))

        assert any("Dry-run" in log for log in logs)
        assert f.exists()  # файл не должен был переименоваться


def test_run_renamer_dry_run_series():
    with tempfile.TemporaryDirectory() as tmpdir:
        folder = Path(tmpdir) / "test season_2"
        folder.mkdir()
        files = []
        for i in range(1, 4):
            f = folder / f"{i} - episode.mkv"
            f.touch()
            files.append(f)

        logs = []
        core.run_renamer(folder, apply=False, callback=lambda message=None,
                                                              progress=None: logs.append(
            message))

        # Проверяем, что Dry-run есть для всех файлов
        dry_runs = [log for log in logs if "Dry-run" in log]
        assert len(dry_runs) == len(files)
