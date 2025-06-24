# src/video_downloader/downloader.py
import yt_dlp

def download_video(url, output_path='%(title)s.%(ext)s'):
    """
    Downloads a video from a given URL.

    :param url: The URL of the video to download.
    :param output_path: The output template for the downloaded file.
    """
    ydl_opts = {
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url]) 