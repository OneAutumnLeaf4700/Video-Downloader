#main.py
from src.video_downloader.downloader import download_video
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        print(f"Starting download for: {video_url}")
        download_video(video_url)
        print("Download finished.")
    else:
        print("Please provide a video URL as a command-line argument.")
        # Example of how to run:
        # python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
