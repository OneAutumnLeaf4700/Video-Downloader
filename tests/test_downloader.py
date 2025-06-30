# tests/test_downloader.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import glob
from video_downloader.downloader import download_video

# Common setup
VIDEO_URL = "https://www.youtube.com/watch?v=4tmuEf9M9Zs"
PLAYLIST_URL = (
    "https://www.youtube.com/watch?v=4tmuEf9M9Zs"
    "&list=PLSkfZAaBHKPQXzdR7ehNl3KRicesPIIso"
)
OUTPUT_DIR = "downloaded_content"


def setup_test_environment(output_pattern):
    """Prepares the directory for a test run."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Use the full pattern for cleanup
    for f in glob.glob(os.path.join(OUTPUT_DIR, output_pattern)):
        os.remove(f)


def cleanup_test_files(output_pattern):
    """Removes files created during a test run."""
    # return # Uncomment this out if you wish to inspect downloaded files
    for f in glob.glob(os.path.join(OUTPUT_DIR, output_pattern)):
        os.remove(f)


def test_download_video_mp4():
    """Tests downloading a standard MP4 video."""
    output_pattern = "test_video.*"
    output_path = os.path.join(OUTPUT_DIR, "test_video.%(ext)s")

    setup_test_environment(output_pattern)
    download_video(VIDEO_URL, output_path=output_path, file_format="mp4")

    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "test_video.mp4"))
    assert len(downloaded_files) > 0, "MP4 video was not downloaded."
    cleanup_test_files(output_pattern)


def test_download_audio_mp3():
    """Tests downloading an audio-only MP3."""
    output_pattern = "test_audio.*"
    output_path = os.path.join(OUTPUT_DIR, "test_audio.%(ext)s")

    setup_test_environment(output_pattern)
    download_video(VIDEO_URL, output_path=output_path, file_format="mp3")

    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "test_audio.mp3"))
    assert len(downloaded_files) > 0, "MP3 audio was not downloaded."
    cleanup_test_files(output_pattern)


def test_download_with_resolution():
    """Tests downloading a video with a specific resolution."""
    output_pattern = "test_resolution.*"
    output_path = os.path.join(OUTPUT_DIR, "test_resolution.%(ext)s")

    setup_test_environment(output_pattern)
    download_video(
        VIDEO_URL, output_path=output_path, file_format="mp4", resolution="480"
    )

    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "test_resolution.mp4"))
    assert (
        len(downloaded_files) > 0
    ), "Video with specific resolution was not downloaded."
    cleanup_test_files(output_pattern)


def test_download_playlist():
    """Tests downloading a small playlist."""
    output_pattern = "playlist_test_*"
    output_path = os.path.join(OUTPUT_DIR, "playlist_test_%(playlist_index)s.%(ext)s")

    setup_test_environment(output_pattern)
    # Note: Downloading playlists can be slow. Using a short, 2-video playlist.
    download_video(
        PLAYLIST_URL, output_path=output_path, is_playlist=True, file_format="mp4"
    )

    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "playlist_test_*.mp4"))
    assert len(downloaded_files) > 1, "Playlist did not download multiple files."
    cleanup_test_files(output_pattern)


if __name__ == "__main__":
    print("Running tests...")
    test_download_video_mp4()
    print("MP4 download test passed.")
    test_download_audio_mp3()
    print("MP3 download test passed.")
    test_download_with_resolution()
    print("Resolution selection test passed.")
    test_download_playlist()
    print("Playlist download test passed.")
    print("\nAll core feature tests passed!")
