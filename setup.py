#!/usr/bin/env python3
# setup.py

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Split on >= or == to get just the package name with version
                    if '>=' in line:
                        requirements.append(line.split('>=')[0])
                    elif '==' in line:
                        requirements.append(line.split('==')[0])
                    else:
                        requirements.append(line)
    return requirements

core_requirements = [
    'PyQt5>=5.15.0',
    'yt-dlp>=2023.1.6'
]

setup(
    name="video-downloader",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple yet powerful video downloader with GUI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Video-Downloader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=core_requirements,
    entry_points={
        "console_scripts": [
            "video-downloader=gui.app:run_app",
        ],
        "gui_scripts": [
            "video-downloader-gui=gui.app:run_app",
        ],
    },
    include_package_data=True,
    package_data={
        "gui": ["*.qss"],
    },
    zip_safe=False,
    keywords="video downloader youtube mp4 mp3 gui pyqt5",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Video-Downloader/issues",
        "Source": "https://github.com/yourusername/Video-Downloader",
        "Documentation": "https://github.com/yourusername/Video-Downloader#readme",
    },
)
