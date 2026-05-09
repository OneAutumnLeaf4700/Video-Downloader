from pathlib import Path

import pytest

from src.utils.folder_utils import (
    DownloadFolderManager,
    ensure_download_folders,
    get_organized_output_path,
)


@pytest.fixture
def manager(tmp_path):
    return DownloadFolderManager(tmp_path)


class TestDownloadFolderManagerInit:
    def test_creates_base_folders(self, tmp_path):
        DownloadFolderManager(tmp_path)
        assert (tmp_path / "videos").is_dir()
        assert (tmp_path / "playlists").is_dir()
        assert (tmp_path / "temp").is_dir()

    def test_idempotent_when_folders_already_exist(self, tmp_path):
        (tmp_path / "videos").mkdir()
        DownloadFolderManager(tmp_path)
        assert (tmp_path / "videos").is_dir()


class TestGetters:
    def test_get_videos_folder(self, manager, tmp_path):
        assert manager.get_videos_folder() == tmp_path / "videos"

    def test_get_playlists_folder(self, manager, tmp_path):
        assert manager.get_playlists_folder() == tmp_path / "playlists"

    def test_get_temp_folder(self, manager, tmp_path):
        assert manager.get_temp_folder() == tmp_path / "temp"


class TestCreatePlaylistFolder:
    def test_creates_playlist_folder_with_uploader(self, manager, tmp_path):
        path = manager.create_playlist_folder("My Playlist", uploader="Alice")
        assert path == tmp_path / "playlists" / "Alice - My Playlist"
        assert path.is_dir()

    def test_creates_playlist_folder_without_uploader(self, manager, tmp_path):
        path = manager.create_playlist_folder("Solo Playlist")
        assert path == tmp_path / "playlists" / "Solo Playlist"
        assert path.is_dir()

    def test_sanitises_invalid_chars_in_name(self, manager, tmp_path):
        path = manager.create_playlist_folder("Bad/Name<With>Chars")
        # Invalid chars replaced with underscores
        assert path.name == "Bad_Name_With_Chars"


class TestCreateVideoSubfolder:
    def test_creates_video_subfolder(self, manager, tmp_path):
        path = manager.create_video_subfolder("Some Video")
        assert path == tmp_path / "videos" / "Some Video"
        assert path.is_dir()

    def test_sanitises_subfolder_name(self, manager):
        path = manager.create_video_subfolder('vid:with"bad<chars>')
        assert all(c not in path.name for c in ':"<>')


class TestSanitizeName:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Plain Name", "Plain Name"),
            ('a/b\\c:d*e?f"g<h>i|j', "a_b_c_d_e_f_g_h_i_j"),
            ("  trimmed.", "trimmed"),
            ("", "Unknown"),
            (None, "Unknown"),
        ],
    )
    def test_sanitize(self, raw, expected):
        assert DownloadFolderManager._sanitize_name(raw) == expected

    def test_truncates_overly_long(self):
        long = "x" * 500
        assert len(DownloadFolderManager._sanitize_name(long)) <= 200


class TestFolderSummary:
    def test_summary_reports_existing_folders(self, manager):
        summary = manager.get_folder_summary()
        assert summary["folders_exist"]["base"] is True
        assert summary["folders_exist"]["videos"] is True
        assert summary["folders_exist"]["playlists"] is True
        assert summary["folders_exist"]["temp"] is True

    def test_summary_counts_video_files(self, manager, tmp_path):
        (tmp_path / "videos" / "a.mp4").write_text("x")
        (tmp_path / "videos" / "b.mp4").write_text("x")
        summary = manager.get_folder_summary()
        assert summary["videos_count"] == 2


class TestCleanupTempFolder:
    def test_removes_files_in_temp(self, manager, tmp_path):
        f = tmp_path / "temp" / "junk.txt"
        f.write_text("x")
        manager.cleanup_temp_folder()
        assert not f.exists()

    def test_removes_subdirectories(self, manager, tmp_path):
        d = tmp_path / "temp" / "sub"
        d.mkdir()
        (d / "x.txt").write_text("x")
        manager.cleanup_temp_folder()
        assert not d.exists()

    def test_noop_when_temp_missing(self, tmp_path):
        m = DownloadFolderManager(tmp_path)
        # Removing the temp folder out from under it
        import shutil
        shutil.rmtree(m.get_temp_folder())
        # Should not raise
        m.cleanup_temp_folder()


class TestEnsureDownloadFolders:
    def test_returns_a_manager(self, tmp_path):
        m = ensure_download_folders(tmp_path)
        assert isinstance(m, DownloadFolderManager)


class TestGetOrganizedOutputPath:
    def test_playlist_path_includes_uploader_and_title(self, tmp_path):
        path = get_organized_output_path(
            tmp_path,
            is_playlist=True,
            playlist_info={"title": "My Playlist", "uploader": "Alice"},
            file_format="mp4",
        )
        assert "Alice - My Playlist" in path
        assert "mp4" in path

    def test_playlist_path_without_uploader(self, tmp_path):
        path = get_organized_output_path(
            tmp_path,
            is_playlist=True,
            playlist_info={"title": "Solo", "uploader": "Unknown"},
            file_format="mp3",
        )
        assert "Solo" in path
        assert "mp3" in path

    def test_video_path_uses_video_title(self, tmp_path):
        path = get_organized_output_path(
            tmp_path,
            video_info={"title": "Some Video"},
            file_format="mp4",
        )
        assert "Some Video" in path
        assert "videos" in path

    def test_fallback_when_no_info(self, tmp_path):
        path = get_organized_output_path(tmp_path, file_format="mp4")
        # Should land in the videos folder under the format
        assert "videos" in path
        assert "mp4" in path
