# src/video_downloader/downloader.py
import yt_dlp
from yt_dlp.utils import DownloadError
import logging

# Configure logging for error reporting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_video(
    url,
    output_path="%(title)s.%(ext)s",
    file_format="mp4",
    resolution=None,
    is_playlist=False,
    progress_hooks=None,
    skip_errors=True,
):
    """
    Downloads a video or playlist from a given URL with specified options.

    :param url: The URL of the video or playlist to download.
    :param output_path: The output template for the downloaded file(s).
    :param file_format: The desired file format ('mp4', 'mp3', etc.).
    :param resolution: The desired video resolution (e.g., '720', '1080').
    :param is_playlist: True to download a playlist, False for a single video.
    :param progress_hooks: A list of functions to be called on download progress.
    :param skip_errors: If True, skip individual videos that fail instead of aborting.
    """
    ydl_opts = {
        "outtmpl": output_path,
        "noplaylist": not is_playlist,
        "postprocessors": [],
        "progress_hooks": progress_hooks or [],
        "ignoreerrors": skip_errors,  # Skip videos that can't be downloaded
        "extract_flat": False,  # Extract complete video info
    }

    if file_format == "mp3":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        )
    else:  # For video formats like mp4, webm, etc.
        format_string = "bestvideo"
        if resolution:
            format_string += f"[height<={resolution}]"
        format_string += "+bestaudio/best"
        ydl_opts["format"] = format_string

        # Add a postprocessor to convert to the desired format
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": file_format,
            }
        )

    # Add error hook to track failed downloads
    failed_downloads = []
    successful_downloads = []
    
    def error_hook(d):
        if d['status'] == 'error':
            error_msg = d.get('error', 'Unknown error')
            video_title = d.get('info_dict', {}).get('title', 'Unknown video')
            failed_downloads.append(f"{video_title}: {error_msg}")
            logger.warning(f"Skipping video '{video_title}' due to error: {error_msg}")
        elif d['status'] == 'finished':
            video_title = d.get('info_dict', {}).get('title', 'Downloaded video')
            successful_downloads.append(video_title)
            logger.info(f"Successfully downloaded: {video_title}")
    
    # Add the error hook to progress hooks
    if progress_hooks is None:
        progress_hooks = []
    progress_hooks.append(error_hook)
    ydl_opts["progress_hooks"] = progress_hooks

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Report summary if there were any failures
        if failed_downloads:
            failed_count = len(failed_downloads)
            success_count = len(successful_downloads)
            total_count = failed_count + success_count
            
            summary_msg = f"Download completed with {success_count}/{total_count} successful downloads."
            if failed_count > 0:
                summary_msg += f" {failed_count} videos were skipped due to errors:"
                for failure in failed_downloads[:5]:  # Show first 5 failures
                    summary_msg += f"\n- {failure}"
                if failed_count > 5:
                    summary_msg += f"\n... and {failed_count - 5} more"
            
            logger.info(summary_msg)
            
            # If all downloads failed and it's not a single video, raise an error
            if failed_count > 0 and success_count == 0 and is_playlist:
                raise DownloadError(f"All videos in playlist failed to download. {summary_msg}")
                
    except DownloadError as e:
        # Extract a cleaner error message from yt-dlp's exception
        if not skip_errors or not is_playlist:
            raise DownloadError(f"Failed to download: {e.args[0]}")
        else:
            logger.error(f"Download error (continuing due to skip_errors=True): {e}")
    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"An unexpected error occurred: {e}")
