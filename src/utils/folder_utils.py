# src/utils/folder_utils.py
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DownloadFolderManager:
    """Manages folder structure for video downloads with standardized organization."""
    
    def __init__(self, base_download_path):
        """
        Initialize the folder manager with a base download path.
        
        :param base_download_path: Base directory for all downloads
        """
        self.base_path = Path(base_download_path)
        self.videos_folder = self.base_path / "videos"
        self.playlists_folder = self.base_path / "playlists"
        self.temp_folder = self.base_path / "temp"
        
        # Ensure all base folders exist
        self._create_base_folders()
    
    def _create_base_folders(self):
        """Create the base folder structure."""
        folders_to_create = [
            self.base_path,
            self.videos_folder,
            self.playlists_folder,
            self.temp_folder
        ]
        
        for folder in folders_to_create:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created/verified folder: {folder}")
            except OSError as e:
                logger.error(f"Failed to create folder {folder}: {e}")
                raise
    
    def get_videos_folder(self):
        """Get the path to the videos folder."""
        return self.videos_folder
    
    def get_playlists_folder(self):
        """Get the path to the playlists folder."""
        return self.playlists_folder
    
    def get_temp_folder(self):
        """Get the path to the temporary downloads folder."""
        return self.temp_folder
    
    def create_playlist_folder(self, playlist_name, uploader=None):
        """
        Create a specific folder for a playlist.
        
        :param playlist_name: Name of the playlist
        :param uploader: Optional uploader name
        :return: Path to the created playlist folder
        """
        # Sanitize names for filesystem safety
        safe_playlist_name = self._sanitize_name(playlist_name)
        
        if uploader:
            safe_uploader = self._sanitize_name(uploader)
            folder_name = f"{safe_uploader} - {safe_playlist_name}"
        else:
            folder_name = safe_playlist_name
        
        playlist_folder = self.playlists_folder / folder_name
        
        try:
            playlist_folder.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created playlist folder: {playlist_folder}")
            return playlist_folder
        except OSError as e:
            logger.error(f"Failed to create playlist folder {playlist_folder}: {e}")
            # Fallback to playlists folder
            return self.playlists_folder
    
    def create_video_subfolder(self, subfolder_name):
        """
        Create a subfolder within the videos directory.
        
        :param subfolder_name: Name of the subfolder
        :return: Path to the created subfolder
        """
        safe_name = self._sanitize_name(subfolder_name)
        subfolder = self.videos_folder / safe_name
        
        try:
            subfolder.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created video subfolder: {subfolder}")
            return subfolder
        except OSError as e:
            logger.error(f"Failed to create video subfolder {subfolder}: {e}")
            # Fallback to videos folder
            return self.videos_folder
    
    def get_folder_summary(self):
        """
        Get a summary of the folder structure and contents.
        
        :return: Dictionary with folder information
        """
        summary = {
            "base_path": str(self.base_path),
            "videos_folder": str(self.videos_folder),
            "playlists_folder": str(self.playlists_folder),
            "temp_folder": str(self.temp_folder),
            "folders_exist": {
                "base": self.base_path.exists(),
                "videos": self.videos_folder.exists(),
                "playlists": self.playlists_folder.exists(),
                "temp": self.temp_folder.exists()
            }
        }
        
        # Count contents if folders exist
        if self.videos_folder.exists():
            try:
                video_count = len([f for f in self.videos_folder.iterdir() if f.is_file()])
                video_subfolders = len([f for f in self.videos_folder.iterdir() if f.is_dir()])
                summary["videos_count"] = video_count
                summary["video_subfolders"] = video_subfolders
            except OSError:
                summary["videos_count"] = "Unknown"
                summary["video_subfolders"] = "Unknown"
        
        if self.playlists_folder.exists():
            try:
                playlist_folders = len([f for f in self.playlists_folder.iterdir() if f.is_dir()])
                summary["playlist_folders"] = playlist_folders
            except OSError:
                summary["playlist_folders"] = "Unknown"
        
        return summary
    
    def cleanup_temp_folder(self):
        """Remove all files from the temporary folder."""
        if not self.temp_folder.exists():
            return
        
        try:
            for item in self.temp_folder.iterdir():
                if item.is_file():
                    item.unlink()
                    logger.info(f"Removed temp file: {item}")
                elif item.is_dir():
                    # Remove directory recursively
                    import shutil
                    shutil.rmtree(item)
                    logger.info(f"Removed temp directory: {item}")
        except OSError as e:
            logger.error(f"Failed to cleanup temp folder: {e}")
    
    @staticmethod
    def _sanitize_name(name):
        """
        Sanitize a name for filesystem safety.
        
        :param name: Original name
        :return: Sanitized name
        """
        import re
        
        if not name:
            return "Unknown"
        
        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', str(name))
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200].strip()
        
        return sanitized if sanitized else "Unknown"


def ensure_download_folders(base_path):
    """
    Utility function to ensure download folder structure exists.
    
    :param base_path: Base path for downloads
    :return: DownloadFolderManager instance
    """
    return DownloadFolderManager(base_path)


def get_organized_output_path(
    base_path, 
    is_playlist=False, 
    playlist_info=None, 
    video_info=None,
    file_format='mp4',
    filename_template="%(title)s.%(ext)s"
):
    """
    Get the appropriate output path for organized downloads.
    
    :param base_path: Base download path
    :param is_playlist: Whether this is a playlist download
    :param playlist_info: Playlist information dictionary
    :param video_info: Video information dictionary
    :param file_format: File format ('mp4' or 'mp3')
    :param filename_template: Template for filename
    :return: Full output path template
    """
    from pathlib import Path
    
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
        playlist_title = DownloadFolderManager._sanitize_name(playlist_info.get('title', 'Unknown Playlist'))
        uploader = DownloadFolderManager._sanitize_name(playlist_info.get('uploader', 'Unknown'))
        
        # Create folder name with uploader if available
        if uploader and uploader != 'Unknown':
            folder_name = f"{uploader} - {playlist_title}"
        else:
            folder_name = playlist_title
            
        playlist_folder = playlists_folder / folder_name
        playlist_folder.mkdir(parents=True, exist_ok=True)
        
        output_path = playlist_folder / filename_template
    elif video_info:
        # Create video-specific folder
        video_title = DownloadFolderManager._sanitize_name(video_info.get('title', 'Unknown Video'))
        video_folder = videos_folder / video_title
        video_folder.mkdir(parents=True, exist_ok=True)
        
        output_path = video_folder / filename_template
    else:
        # Fallback to videos folder if no info is available
        output_path = videos_folder / filename_template
    
    return str(output_path)
