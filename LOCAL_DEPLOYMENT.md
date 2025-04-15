# TasVID YouTube Downloader - Local Deployment Guide

This guide will help you deploy the TasVID YouTube downloader application on your local machine.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- ffmpeg (for video processing)

## Quick Start

1. Extract the `tasvid_complete.tar.gz` file to a directory of your choice
2. Open a terminal/command prompt in that directory
3. Make the deployment script executable:
   ```
   chmod +x deploy_local.sh
   ```
4. Run the deployment script:
   ```
   ./deploy_local.sh
   ```
5. Access the application at http://localhost:5000

## Manual Installation

If you prefer to install manually or are using Windows:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a downloads directory:
   ```
   mkdir -p downloads
   ```

5. Start the application:
   ```
   gunicorn --bind 0.0.0.0:5000 app:app
   ```
   - On Windows (if gunicorn doesn't work):
     ```
     python app.py
     ```

6. Access the application at http://localhost:5000

## Application Features

- YouTube video downloading with format selection
- Bypass mechanisms for encrypted URLs, token expiry, chunked streaming, etc.
- Video compression and format conversion
- Download history tracking
- Batch downloads
- Playlist downloading
- Video trimming
- Audio extraction
- File organization and encryption

## Troubleshooting

- If you encounter port conflicts, change the port number in the command:
  ```
  gunicorn --bind 0.0.0.0:8080 app:app
  ```

- If ffmpeg is not in your PATH, you may need to specify its location in the settings page

- For Windows users who have issues with gunicorn, you can use the Flask development server:
  ```
  python app.py
  ```

## Security Considerations

- This application is designed for local use
- Be aware of YouTube's terms of service when downloading content
- Downloaded files are stored in the 'downloads' directory by default
