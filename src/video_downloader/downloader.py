# src/video_downloader/downloader.py
import yt_dlp
from yt_dlp.utils import DownloadError
import logging
import os
import re
from pathlib import Path


# Configure logging for error reporting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    :param filename: The original filename
    :return: A sanitized filename safe for use in file systems
    """
    # Remove or replace invalid characters for Windows/Unix file systems
    invalid_chars = r'[<>:"/\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length to avoid filesystem issues
    if len(sanitized) > 200:
        sanitized = sanitized[:200].strip()
    
    return sanitized if sanitized else "Unknown"


def get_playlist_info(url):
    """
    Extract playlist information without downloading.
    
    :param url: The playlist URL
    :return: Dictionary with playlist info (title, uploader, count, etc.)
    """
    ydl_opts = {
        'extract_flat': True,  # Don't extract individual video info
        'quiet': True,  # Suppress output
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                return None
                
            # Check if it's actually a playlist
            if info.get('_type') != 'playlist':
                return None
                
            return {
                'title': info.get('title', 'Unknown Playlist'),
                'uploader': info.get('uploader', 'Unknown'),
                'description': info.get('description', ''),
                'entry_count': len(info.get('entries', [])),
                'id': info.get('id', ''),
                'webpage_url': info.get('webpage_url', url)
            }
    except Exception as e:
        print(f"Warning: Could not extract playlist info: {e}")
        return None


def get_video_info(url):
    """
    Extract video information without downloading.
    
    :param url: The video URL
    :return: Dictionary with video info (title, uploader, duration, etc.)
    """
    ydl_opts = {
        'quiet': True,  # Suppress output
        'no_warnings': True,  # Suppress warnings
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                return None
                
            # For single videos or if it's the first video of a playlist
            if info.get('_type') == 'playlist':
                # If URL points to a playlist but we want single video info
                # Get the first video info
                entries = info.get('entries', [])
                if entries:
                    info = entries[0]
                else:
                    return None
                    
            return {
                'title': info.get('title', 'Unknown Video'),
                'uploader': info.get('uploader', 'Unknown'),
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'id': info.get('id', ''),
                'webpage_url': info.get('webpage_url', url)
            }
    except Exception as e:
        print(f"Warning: Could not extract video info: {e}")
        return None


def create_organized_folders(base_path, is_playlist=False, playlist_info=None, video_info=None, file_format='mp4'):
    """
    Create organized folder structure for downloads.
    
    :param base_path: Base download directory
    :param is_playlist: Whether this is a playlist download
    :param playlist_info: Dictionary with playlist information
    :param video_info: Dictionary with video information
    :param file_format: Video or audio format ('mp4' or 'mp3')
    :return: Path where files should be downloaded
    """
    base_path = Path(base_path)
    
    # Create format-specific base folders
    format_folder = base_path / file_format.lower()
    videos_folder = format_folder / "videos"
    playlists_folder = format_folder / "playlists"
    
    # Ensure base folders exist
    videos_folder.mkdir(parents=True, exist_ok=True)
    playlists_folder.mkdir(parents=True, exist_ok=True)
    
    if is_playlist and playlist_info:
        # Create playlist-specific folder
        playlist_title = sanitize_filename(playlist_info['title'])
        uploader = sanitize_filename(playlist_info.get('uploader', 'Unknown'))
        
        # Create folder name with uploader if available
        if uploader and uploader != 'Unknown':
            folder_name = f"{uploader} - {playlist_title}"
        else:
            folder_name = playlist_title
            
        playlist_folder = playlists_folder / folder_name
        playlist_folder.mkdir(parents=True, exist_ok=True)
        
        return playlist_folder
    elif video_info:
        # Create video-specific folder
        video_title = sanitize_filename(video_info['title'])
        video_folder = videos_folder / video_title
        video_folder.mkdir(parents=True, exist_ok=True)
        
        return video_folder
    else:
        # Fallback to videos folder if no info is available
        return videos_folder


def download_video(
    url,
    output_path="%(title)s.%(ext)s",
    file_format="mp4",
    resolution=None,
    is_playlist=False,
    progress_hooks=None,
    skip_errors=True,
    organize_folders=True,
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
    :param organize_folders: Whether to organize downloads into folders.
    """
    
    # Handle folder organization
    final_output_path = output_path
    playlist_info = None
    video_info = None
    
    if organize_folders:
        # Extract base directory from output path
        base_dir = os.path.dirname(output_path) if "/" in output_path or "\\" in output_path else "."
        filename_template = os.path.basename(output_path)
        
        # Get playlist info if it's a playlist
        if is_playlist:
            print("Retrieving playlist information...")
            playlist_info = get_playlist_info(url)
            if playlist_info:
                print(f"Found playlist: '{playlist_info['title']}' by {playlist_info['uploader']} ({playlist_info['entry_count']} videos)")
        else:
            # Get video info for single video
            print("Retrieving video information...")
            video_info = get_video_info(url)
            if video_info:
                print(f"Found video: '{video_info['title']}' by {video_info['uploader']}")
        
        # Create organized folder structure
        download_folder = create_organized_folders(
            base_dir, 
            is_playlist, 
            playlist_info, 
            video_info, 
            file_format
        )
        final_output_path = str(download_folder / filename_template)
        
        print(f"Downloads will be saved to: {download_folder}")
    
    ydl_opts = {
        "outtmpl": final_output_path,
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
        # Prefer MP4-compatible streams and merge to a single MP4
        if resolution:
            format_string = (
                f"bv*[ext=mp4][height<={resolution}]+ba[ext=m4a]/b[ext=mp4]/b"
            )
        else:
            format_string = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b"
        ydl_opts["format"] = format_string

        # Ensure final output is a single MP4 (merge/remux instead of re-encode)
        ydl_opts["merge_output_format"] = "mp4"
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegVideoRemuxer",
                "preferedformat": "mp4",
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
