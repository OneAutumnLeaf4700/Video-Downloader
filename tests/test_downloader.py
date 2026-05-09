from unittest.mock import MagicMock, patch

import pytest

from src.video_downloader.downloader import (
    create_organized_folders,
    download_video,
    get_playlist_info,
    get_video_info,
    sanitize_filename,
)


class TestSanitizeFilename:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("plain.mp4", "plain.mp4"),
            ('foo/bar:baz<x>"y"|z?.mp4', "foo_bar_baz_x__y__z_.mp4"),
            ("  spaced .", "spaced"),
            ("", "Unknown"),
        ],
    )
    def test_sanitize(self, raw, expected):
        assert sanitize_filename(raw) == expected

    def test_truncates_long(self):
        long = "x" * 500
        assert len(sanitize_filename(long)) <= 200


class TestCreateOrganizedFolders:
    def test_creates_format_folder(self, tmp_path):
        path = create_organized_folders(tmp_path, file_format="mp4")
        assert path == tmp_path / "mp4"
        assert path.is_dir()

    def test_lowercases_format(self, tmp_path):
        path = create_organized_folders(tmp_path, file_format="MP3")
        assert path.name == "mp3"


class TestGetPlaylistInfo:
    def test_returns_dict_for_playlist(self):
        fake_info = {
            "_type": "playlist",
            "title": "My Playlist",
            "uploader": "Alice",
            "description": "desc",
            "entries": [{}, {}, {}],
            "id": "PL123",
            "webpage_url": "https://example.com/playlist",
        }
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = fake_info
            result = get_playlist_info("https://example.com/playlist")
        assert result == {
            "title": "My Playlist",
            "uploader": "Alice",
            "description": "desc",
            "entry_count": 3,
            "id": "PL123",
            "webpage_url": "https://example.com/playlist",
        }

    def test_returns_none_for_non_playlist(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = {"_type": "video", "title": "x"}
            assert get_playlist_info("https://example.com/v") is None

    def test_returns_none_when_no_info(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = None
            assert get_playlist_info("https://example.com/v") is None

    def test_returns_none_on_exception(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.side_effect = RuntimeError("boom")
            assert get_playlist_info("https://example.com/v") is None


class TestGetVideoInfo:
    def test_returns_dict_for_single_video(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = {
                "title": "Some Video",
                "uploader": "Alice",
                "description": "desc",
                "duration": 120,
                "id": "abc",
                "webpage_url": "https://example.com/v",
            }
            result = get_video_info("https://example.com/v")
        assert result["title"] == "Some Video"
        assert result["duration"] == 120

    def test_falls_back_to_first_entry_for_playlist_url(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = {
                "_type": "playlist",
                "entries": [
                    {"title": "First", "uploader": "Bob"},
                    {"title": "Second", "uploader": "Bob"},
                ],
            }
            result = get_video_info("https://example.com/playlist")
        assert result["title"] == "First"

    def test_returns_none_for_empty_playlist(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.return_value = {"_type": "playlist", "entries": []}
            assert get_video_info("https://example.com/p") is None

    def test_returns_none_on_exception(self):
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            instance = MockYDL.return_value.__enter__.return_value
            instance.extract_info.side_effect = RuntimeError("boom")
            assert get_video_info("https://example.com/v") is None


class TestDownloadVideoOptions:
    """Verify that download_video builds the right yt-dlp option dict for each
    format / resolution combination, by capturing the YoutubeDL constructor arg.
    """

    def _capture_opts(self, url, **kwargs):
        captured = {}
        with patch("src.video_downloader.downloader.yt_dlp.YoutubeDL") as MockYDL:
            def grab(opts):
                captured.update(opts)
                instance = MagicMock()
                instance.__enter__.return_value = instance
                instance.__exit__.return_value = False
                instance.download = MagicMock()
                return instance

            MockYDL.side_effect = grab
            download_video(url, organize_folders=False, **kwargs)
        return captured

    def test_mp4_default_uses_merge_to_mp4(self):
        opts = self._capture_opts("https://example.com/v", file_format="mp4")
        assert opts["merge_output_format"] == "mp4"
        assert "bv*[ext=mp4]+ba[ext=m4a]" in opts["format"]
        # FFmpegVideoRemuxer postprocessor present
        assert any(p["key"] == "FFmpegVideoRemuxer" for p in opts["postprocessors"])

    def test_mp4_with_resolution_caps_height(self):
        opts = self._capture_opts(
            "https://example.com/v", file_format="mp4", resolution="720"
        )
        assert "[height<=720]" in opts["format"]

    def test_mp3_uses_audio_extractor(self):
        opts = self._capture_opts("https://example.com/v", file_format="mp3")
        assert opts["format"] == "bestaudio/best"
        assert any(p["key"] == "FFmpegExtractAudio" for p in opts["postprocessors"])
        assert all(
            p.get("preferredcodec", "mp3") == "mp3"
            for p in opts["postprocessors"]
            if p["key"] == "FFmpegExtractAudio"
        )

    def test_noplaylist_inverts_is_playlist(self):
        single = self._capture_opts(
            "https://example.com/v", file_format="mp4", is_playlist=False
        )
        playlist = self._capture_opts(
            "https://example.com/v", file_format="mp4", is_playlist=True
        )
        assert single["noplaylist"] is True
        assert playlist["noplaylist"] is False

    def test_progress_hooks_passed_through(self):
        hook = MagicMock()
        opts = self._capture_opts(
            "https://example.com/v",
            file_format="mp4",
            progress_hooks=[hook],
        )
        # The user hook is included plus the internal error_hook
        assert hook in opts["progress_hooks"]
        assert len(opts["progress_hooks"]) >= 2
