# tests/test_downloader.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import glob
from video_downloader.downloader import download_video

# Common setup
VIDEO_URL = "https://www.youtube.com/watch?v=4tmuEf9M9Zs&ab_channel=ketfut"
OUTPUT_DIR = "downloaded_content"

def setup_test_environment(output_pattern):
    """Prepares the directory for a test run."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for f in glob.glob(os.path.join(OUTPUT_DIR, output_pattern)):
        os.remove(f)

def cleanup_test_files(output_pattern):
    """Removes files created during a test run."""
    for f in glob.glob(os.path.join(OUTPUT_DIR, output_pattern)):
        os.remove(f)

def test_download_video_mp4():
    """Tests downloading a standard MP4 video."""
    output_pattern = "test_video.*"
    output_path = os.path.join(OUTPUT_DIR, "test_video.%(ext)s")
    
    setup_test_environment(output_pattern)
    download_video(VIDEO_URL, output_path=output_path, file_format='mp4')
    
    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "test_video.mp4"))
    assert len(downloaded_files) > 0, "MP4 video was not downloaded."
    cleanup_test_files(output_pattern)

def test_download_audio_mp3():
    """Tests downloading an audio-only MP3."""
    output_pattern = "test_audio.*"
    output_path = os.path.join(OUTPUT_DIR, "test_audio.%(ext)s")
    
    setup_test_environment(output_pattern)
    download_video(VIDEO_URL, output_path=output_path, file_format='mp3')
    
    downloaded_files = glob.glob(os.path.join(OUTPUT_DIR, "test_audio.mp3"))
    assert len(downloaded_files) > 0, "MP3 audio was not downloaded."
    cleanup_test_files(output_pattern)

if __name__ == "__main__":
    print("Running tests...")
    test_download_video_mp4()
    print("MP4 download test passed.")
    test_download_audio_mp3()
    print("MP3 download test passed.")
    print("All tests passed!") 