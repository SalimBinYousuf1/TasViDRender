# TasVID YouTube Downloader - Deployment Guide

## Overview

TasVID is a fully-featured YouTube downloader web application built with Flask, yt-dlp, and ffmpeg. It provides a clean, modern interface for downloading YouTube videos in various formats and resolutions, with advanced features like compression, batch downloads, video trimming, and more.

## Features

- **Core Functionality**:
  - Download YouTube videos in various formats and resolutions
  - Extract audio from videos
  - Compress videos using CRF (Constant Rate Factor)
  - Track download history
  - Customize settings

- **Advanced Bypass Mechanisms**:
  - Handles encrypted URLs and dynamic signatures
  - Manages token expiry issues
  - Processes chunked streaming
  - Implements rate limiting protection
  - Detects and handles CAPTCHA challenges
  - Supports login for restricted videos

- **Bonus Features**:
  - Batch downloads
  - Playlist downloads
  - Video trimming
  - Audio volume control
  - File renaming
  - Auto-categorization
  - Cloud uploads
  - File encryption
  - Notifications

## Requirements

- Python 3.8+
- Flask
- yt-dlp
- ffmpeg
- Additional Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/TasVID.git
   cd TasVID
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install ffmpeg:
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Configuration

1. The application stores settings, download history, and user credentials in the `instance` directory.
2. Default download locations:
   - **Desktop**: `~/Desktop/TasVID/`
   - **Mobile**: Device gallery/downloads folder

## Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Deployment Options

### Local Deployment

The application runs on `0.0.0.0:5000` by default, making it accessible on your local network.

### Production Deployment

For production deployment, consider using:

1. **Gunicorn with Nginx**:
   ```
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```
   
   Configure Nginx as a reverse proxy.

2. **Docker**:
   A Dockerfile is provided for containerized deployment.

## Security Considerations

1. The application includes optional authentication with email-based OTP.
2. For production use, consider:
   - Using HTTPS
   - Implementing rate limiting
   - Setting up proper user authentication
   - Restricting access to sensitive endpoints

## Troubleshooting

1. **Download Issues**:
   - Ensure ffmpeg is properly installed
   - Check network connectivity
   - Verify YouTube URL is valid and accessible

2. **Performance Issues**:
   - Adjust compression settings
   - Limit concurrent downloads
   - Ensure sufficient disk space

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- yt-dlp for YouTube extraction capabilities
- ffmpeg for video processing
- Flask for the web framework
