<!-- README.md -->
# Video Downloader

![App Banner](docs/screenshots/banner.png)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A simple yet powerful video downloader with a graphical user interface built using Python and PyQt5. This tool allows you to download videos and playlists from hundreds of websites.

---

## Screenshots

> **Tip:** Place your screenshots in the `docs/screenshots/` folder. Replace the placeholder images below with your own!

### Main Window
![Main Window](docs/screenshots/main_window.png)

### Download in Progress
![Download Progress](docs/screenshots/progress.png)

### Error Handling
![Error Dialog](docs/screenshots/error.png)

---

## Features

- **Multi-threaded Downloads**: Download multiple videos simultaneously with configurable worker threads
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Easy-to-Use GUI**: A clean and modern interface built with PyQt5
- **Multiple Site Support**: Powered by `yt-dlp`, supports 100+ video hosting sites
- **Format Selection**: Download videos as `MP4` or extract audio as `MP3`
- **Resolution Options**: Choose your preferred video quality (1080p, 720p, etc.)
- **Playlist Downloads**: Download entire playlists with a single click
- **Custom Save Location**: Choose where you want to save your downloaded files
- **Real-time Progress**: Progress bars and queue display keep you updated
- **Organized Storage**: Automatic folder organization by format and content type
- **Error Handling**: Robust error handling with retry mechanisms
- **Comprehensive Testing**: Full test suite with pytest, flake8, Black, and mypy

## Setup and Usage

Follow these steps to get the application running on your local machine.

## Installation

### Option 1: From Source (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Video-Downloader.git
   cd Video-Downloader
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Option 2: Using pip

```bash
pip install video-downloader
video-downloader-gui
```

### Option 3: Pre-built Executables

Download the latest release from the [Releases page](https://github.com/yourusername/Video-Downloader/releases) for your platform.

## Development Setup

If you want to contribute or modify the code:

1. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

2. **Run tests**:
   ```bash
   python run_tests.py
   ```

3. **Run linting**:
   ```bash
   python run_tests.py --lint-only
   ```

4. **Build executable**:
   ```bash
   python build.py
   ```

## How to Use

1. **Launch the application** using one of the installation methods above
2. **Paste the video or playlist URL** into the URL input field
3. **Choose your desired download location** using the "Browse" button
4. **Select the format** (MP4/MP3) and resolution
5. **Check "Download as playlist"** if the URL is a playlist
6. **Click "Download"** and watch the progress in the queue display
7. **Multiple downloads** can be queued simultaneously for faster processing

## Prerequisites

- **Python 3.8+**: Required for running from source
- **ffmpeg**: Required for video/audio conversion (download from [ffmpeg.org](https://ffmpeg.org/download.html))
- **Internet connection**: For downloading videos

## Supported Sites

This application supports 100+ video hosting sites through yt-dlp, including:
- YouTube
- Vimeo
- Twitch
- Facebook
- Instagram
- Twitter
- TikTok
- And many more!

## Technical Features

### Multi-threaded Architecture
- **Concurrent Downloads**: Download multiple videos simultaneously using configurable worker threads
- **Queue Management**: Intelligent task queuing with priority handling
- **Thread Safety**: Thread-safe operations with proper locking mechanisms
- **Resource Management**: Automatic cleanup and memory management

### Cross-platform Compatibility
- **Windows**: Native Windows executable with proper GUI integration
- **macOS**: macOS app bundle with proper code signing support
- **Linux**: AppImage and native package support
- **Universal**: Single codebase runs on all platforms

### Quality Assurance
- **Comprehensive Testing**: Unit tests, integration tests, and GUI tests
- **Code Quality**: Automated linting with flake8 and formatting with Black
- **Type Safety**: Full type checking with mypy
- **CI/CD**: Automated testing and building across all platforms

### Performance Optimization
- **Efficient Downloads**: Optimized download strategies and error handling
- **Memory Management**: Proper resource cleanup and memory usage
- **Progress Tracking**: Real-time progress updates with minimal overhead
- **Error Recovery**: Robust error handling with automatic retry mechanisms