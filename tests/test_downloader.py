# tests/test_downloader.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import glob
from video_downloader.downloader import download_video

def test_download_video():
    url = "https://www.youtube.com/watch?v=4tmuEf9M9Zs&ab_channel=ketfut"
    output_dir = "downloaded_content"
    output_pattern = os.path.join(output_dir, "test_sample.%(ext)s")
    os.makedirs(output_dir, exist_ok=True)
    for f in glob.glob(os.path.join(output_dir, "test_sample.*")):
        os.remove(f)
    download_video(url, output_path=output_pattern)
    downloaded_files = glob.glob(os.path.join(output_dir, "test_sample.*"))
    assert len(downloaded_files) > 0, "No file was downloaded."
    #Remove the downloaded file
    for f in downloaded_files:
        os.remove(f)

if __name__ == "__main__":
    test_download_video() 