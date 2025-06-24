# src/video_downloader/downloader.py
import yt_dlp
from yt_dlp.utils import DownloadError

def download_video(url, output_path='%(title)s.%(ext)s', file_format='mp4', resolution=None, is_playlist=False, progress_hooks=None):
    """
    Downloads a video or playlist from a given URL with specified options.

    :param url: The URL of the video or playlist to download.
    :param output_path: The output template for the downloaded file(s).
    :param file_format: The desired file format ('mp4', 'mp3', etc.).
    :param resolution: The desired video resolution (e.g., '720', '1080').
    :param is_playlist: True to download a playlist, False for a single video.
    :param progress_hooks: A list of functions to be called on download progress.
    """
    ydl_opts = {
        'outtmpl': output_path,
        'noplaylist': not is_playlist,
        'postprocessors': [],
        'progress_hooks': progress_hooks or [],
    }

    if file_format == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })
    else: # For video formats like mp4, webm, etc.
        format_string = 'bestvideo'
        if resolution:
            format_string += f'[height<={resolution}]'
        format_string += '+bestaudio/best'
        ydl_opts['format'] = format_string
        
        # Add a postprocessor to convert to the desired format
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': file_format,
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as e:
        # Extract a cleaner error message from yt-dlp's exception
        raise DownloadError(f"Failed to download: {e.args[0]}")
    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"An unexpected error occurred: {e}") 