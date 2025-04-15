# TasVID YouTube Downloader - Additional Features Module

import os
import sys
import json
import time
import uuid
import shutil
import subprocess
from datetime import datetime, timedelta
import ffmpeg
import yt_dlp
from threading import Thread

class AdditionalFeatures:
    def __init__(self, app_config, downloader):
        self.app_config = app_config
        self.downloader = downloader
        self.scheduled_downloads = {}
        self.batch_downloads = {}
        
        # Create necessary directories
        self.temp_dir = os.path.join(os.path.dirname(app_config['DOWNLOAD_HISTORY_FILE']), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load scheduled downloads
        self.scheduled_file = os.path.join(os.path.dirname(app_config['DOWNLOAD_HISTORY_FILE']), 'scheduled.json')
        self.load_scheduled_downloads()
        
        # Start scheduler thread
        self.scheduler_running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def load_scheduled_downloads(self):
        """Load scheduled downloads from file"""
        if os.path.exists(self.scheduled_file):
            try:
                with open(self.scheduled_file, 'r') as f:
                    self.scheduled_downloads = json.load(f)
            except:
                self.scheduled_downloads = {}
    
    def save_scheduled_downloads(self):
        """Save scheduled downloads to file"""
        with open(self.scheduled_file, 'w') as f:
            json.dump(self.scheduled_downloads, f)
    
    def _scheduler_loop(self):
        """Background thread to check and process scheduled downloads"""
        while self.scheduler_running:
            now = datetime.now()
            to_remove = []
            
            for download_id, download in self.scheduled_downloads.items():
                scheduled_time = datetime.fromisoformat(download['scheduled_time'])
                if now >= scheduled_time:
                    # Time to start this download
                    print(f"Starting scheduled download: {download['url']}")
                    
                    # Start the download
                    self.downloader.download_video(
                        download['url'],
                        download['format_id'],
                        download['resolution'],
                        download['compression'],
                        download['download_dir'],
                        download.get('cookies_file')
                    )
                    
                    # Mark for removal
                    to_remove.append(download_id)
            
            # Remove completed scheduled downloads
            for download_id in to_remove:
                del self.scheduled_downloads[download_id]
            
            # Save changes if any
            if to_remove:
                self.save_scheduled_downloads()
            
            # Sleep for a bit
            time.sleep(60)  # Check every minute
    
    def schedule_download(self, url, format_id, resolution, compression, download_dir, 
                         scheduled_time, cookies_file=None):
        """Schedule a download for later"""
        download_id = str(uuid.uuid4())
        
        # Store the scheduled download
        self.scheduled_downloads[download_id] = {
            'url': url,
            'format_id': format_id,
            'resolution': resolution,
            'compression': compression,
            'download_dir': download_dir,
            'scheduled_time': scheduled_time.isoformat(),
            'cookies_file': cookies_file
        }
        
        # Save to file
        self.save_scheduled_downloads()
        
        return {
            'success': True,
            'download_id': download_id,
            'message': f'Download scheduled for {scheduled_time.strftime("%Y-%m-%d %H:%M:%S")}'
        }
    
    def cancel_scheduled_download(self, download_id):
        """Cancel a scheduled download"""
        if download_id in self.scheduled_downloads:
            del self.scheduled_downloads[download_id]
            self.save_scheduled_downloads()
            return {
                'success': True,
                'message': 'Scheduled download cancelled'
            }
        else:
            return {
                'success': False,
                'message': 'Scheduled download not found'
            }
    
    def get_scheduled_downloads(self):
        """Get list of scheduled downloads"""
        return {
            'success': True,
            'scheduled_downloads': self.scheduled_downloads
        }
    
    def batch_download(self, urls, format_id, resolution, compression, download_dir, cookies_file=None):
        """Download multiple videos in batch"""
        batch_id = str(uuid.uuid4())
        
        # Initialize batch tracking
        self.batch_downloads[batch_id] = {
            'status': 'starting',
            'total': len(urls),
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'downloads': {}
        }
        
        # Start batch download in a separate thread
        thread = Thread(
            target=self._batch_download_thread,
            args=(batch_id, urls, format_id, resolution, compression, download_dir, cookies_file)
        )
        thread.daemon = True
        thread.start()
        
        return {
            'success': True,
            'batch_id': batch_id,
            'message': f'Batch download of {len(urls)} videos started'
        }
    
    def _batch_download_thread(self, batch_id, urls, format_id, resolution, compression, download_dir, cookies_file):
        """Thread function to handle batch downloads"""
        # Process each URL
        for url in urls:
            # Update batch status
            self.batch_downloads[batch_id]['in_progress'] += 1
            
            try:
                # Start the download
                result = self.downloader.download_video(
                    url,
                    format_id,
                    resolution,
                    compression,
                    download_dir,
                    cookies_file
                )
                
                if result['success']:
                    # Track this download in the batch
                    download_id = result['download_id']
                    self.batch_downloads[batch_id]['downloads'][download_id] = {
                        'url': url,
                        'status': 'in_progress'
                    }
                    
                    # Wait for download to complete
                    self._wait_for_download(batch_id, download_id)
                else:
                    # Download failed to start
                    self.batch_downloads[batch_id]['failed'] += 1
            except Exception as e:
                print(f"Error in batch download: {str(e)}")
                self.batch_downloads[batch_id]['failed'] += 1
            
            # Update batch status
            self.batch_downloads[batch_id]['in_progress'] -= 1
        
        # Mark batch as completed
        self.batch_downloads[batch_id]['status'] = 'completed'
    
    def _wait_for_download(self, batch_id, download_id):
        """Wait for a download to complete and update batch status"""
        max_checks = 600  # Maximum number of checks (10 minutes at 1 check per second)
        checks = 0
        
        while checks < max_checks:
            # Get download status
            if download_id in self.downloader.active_downloads:
                status = self.downloader.active_downloads[download_id]['status']
                
                # Update batch tracking
                self.batch_downloads[batch_id]['downloads'][download_id]['status'] = status
                
                # Check if download is complete or failed
                if status == 'completed':
                    self.batch_downloads[batch_id]['completed'] += 1
                    return
                elif status == 'error' or status == 'cancelled':
                    self.batch_downloads[batch_id]['failed'] += 1
                    return
            else:
                # Download not found
                self.batch_downloads[batch_id]['failed'] += 1
                return
            
            # Wait before checking again
            time.sleep(1)
            checks += 1
        
        # If we get here, the download timed out
        self.batch_downloads[batch_id]['failed'] += 1
    
    def get_batch_status(self, batch_id):
        """Get status of a batch download"""
        if batch_id in self.batch_downloads:
            return {
                'success': True,
                'batch_info': self.batch_downloads[batch_id]
            }
        else:
            return {
                'success': False,
                'message': 'Batch download not found'
            }
    
    def trim_video(self, video_path, start_time, end_time, output_filename=None):
        """Trim a video to specified start and end times"""
        try:
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.basename(video_path)
                name, ext = os.path.splitext(base_name)
                output_filename = f"{name}_trimmed{ext}"
            
            output_path = os.path.join(os.path.dirname(video_path), output_filename)
            
            # Convert time strings to seconds
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            # Calculate duration
            duration = end_seconds - start_seconds
            
            # Use ffmpeg to trim the video
            (
                ffmpeg
                .input(video_path, ss=start_seconds)
                .output(output_path, t=duration, c='copy')
                .run(quiet=True, overwrite_output=True)
            )
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'Video trimmed successfully'
            }
        except Exception as e:
            print(f"Error trimming video: {str(e)}")
            return {
                'success': False,
                'message': f'Error trimming video: {str(e)}'
            }
    
    def _time_to_seconds(self, time_str):
        """Convert time string (HH:MM:SS or MM:SS) to seconds"""
        parts = time_str.split(':')
        
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            try:
                return int(time_str)  # Seconds only
            except:
                return 0
    
    def adjust_audio_volume(self, video_path, volume_factor, output_filename=None):
        """Adjust audio volume of a video"""
        try:
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.basename(video_path)
                name, ext = os.path.splitext(base_name)
                output_filename = f"{name}_volume{ext}"
            
            output_path = os.path.join(os.path.dirname(video_path), output_filename)
            
            # Use ffmpeg to adjust volume
            (
                ffmpeg
                .input(video_path)
                .output(output_path, af=f"volume={volume_factor}")
                .run(quiet=True, overwrite_output=True)
            )
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'Audio volume adjusted successfully'
            }
        except Exception as e:
            print(f"Error adjusting audio volume: {str(e)}")
            return {
                'success': False,
                'message': f'Error adjusting audio volume: {str(e)}'
            }
    
    def extract_audio(self, video_path, audio_format='mp3', quality='192', output_filename=None):
        """Extract audio from a video"""
        try:
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.basename(video_path)
                name, _ = os.path.splitext(base_name)
                output_filename = f"{name}.{audio_format}"
            
            output_path = os.path.join(os.path.dirname(video_path), output_filename)
            
            # Use ffmpeg to extract audio
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec=self._get_audio_codec(audio_format), ab=f"{quality}k")
                .run(quiet=True, overwrite_output=True)
            )
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'Audio extracted successfully'
            }
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            return {
                'success': False,
                'message': f'Error extracting audio: {str(e)}'
            }
    
    def _get_audio_codec(self, format):
        """Get ffmpeg audio codec for format"""
        codecs = {
            'mp3': 'libmp3lame',
            'ogg': 'libvorbis',
            'aac': 'aac',
            'wav': 'pcm_s16le',
            'flac': 'flac'
        }
        return codecs.get(format, 'libmp3lame')
    
    def rename_file(self, file_path, new_name):
        """Rename a file"""
        try:
            dir_path = os.path.dirname(file_path)
            ext = os.path.splitext(file_path)[1]
            new_path = os.path.join(dir_path, f"{new_name}{ext}")
            
            # Rename the file
            os.rename(file_path, new_path)
            
            # Update history if this is a downloaded file
            self._update_history_filename(file_path, new_path)
            
            return {
                'success': True,
                'new_path': new_path,
                'message': 'File renamed successfully'
            }
        except Exception as e:
            print(f"Error renaming file: {str(e)}")
            return {
                'success': False,
                'message': f'Error renaming file: {str(e)}'
            }
    
    def _update_history_filename(self, old_path, new_path):
        """Update download history with new filename"""
        history_file = self.app_config['DOWNLOAD_HISTORY_FILE']
        
        # Load existing history
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                # Update matching entries
                for entry in history:
                    if entry.get('path') == old_path:
                        entry['path'] = new_path
                        # Update title based on new filename
                        entry['title'] = os.path.basename(new_path).split('.')[0]
                
                # Save updated history
                with open(history_file, 'w') as f:
                    json.dump(history, f)
            except:
                pass
    
    def auto_categorize(self, video_info):
        """Auto-categorize a video based on metadata"""
        # This is a simplified implementation
        # A real implementation would use more sophisticated categorization
        
        title = video_info.get('title', '').lower()
        tags = video_info.get('tags', [])
        description = video_info.get('description', '').lower()
        
        # Define category keywords
        categories = {
            'music': ['music', 'song', 'audio', 'concert', 'band', 'singer', 'album'],
            'gaming': ['game', 'gaming', 'gameplay', 'playthrough', 'walkthrough', 'xbox', 'playstation', 'nintendo'],
            'education': ['education', 'tutorial', 'learn', 'course', 'lecture', 'how to', 'guide'],
            'entertainment': ['entertainment', 'funny', 'comedy', 'prank', 'challenge', 'vlog'],
            'news': ['news', 'report', 'politics', 'current events', 'breaking'],
            'sports': ['sports', 'football', 'soccer', 'basketball', 'baseball', 'nfl', 'nba', 'mlb'],
            'technology': ['tech', 'technology', 'review', 'unboxing', 'smartphone', 'computer'],
            'travel': ['travel', 'vlog', 'tour', 'trip', 'vacation', 'destination']
        }
        
        # Check title, tags, and description for category keywords
        scores = {category: 0 for category in categories}
        
        for category, keywords in categories.items():
            # Check title (higher weight)
            for keyword in keywords:
                if keyword in title:
                    scores[category] += 3
            
            # Check tags (medium weight)
            for tag in tags:
                tag = tag.lower()
                for keyword in keywords:
                    if keyword in tag:
                        scores[category] += 2
            
            # Check description (lower weight)
            for keyword in keywords:
                if keyword in description:
                    scores[category] += 1
        
        # Get category with highest score
        max_score = 0
        best_category = 'other'
        
        for category, score in scores.items():
            if score > max_score:
                max_score = score
                best_category = category
        
        return best_category
    
    def auto_organize(self, file_path, video_info, organization_type='category'):
        """Auto-organize downloads by date or category"""
        try:
            if organization_type == 'category':
                # Categorize the video
                category = self.auto_categorize(video_info)
                
                # Create category directory
                base_dir = os.path.dirname(os.path.dirname(file_path))
                category_dir = os.path.join(base_dir, 'Categories', category)
                os.makedirs(category_dir, exist_ok=True)
                
                # Move file to category directory
                new_path = os.path.join(category_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                # Update history
                self._update_history_filename(file_path, new_path)
                
                return {
                    'success': True,
                    'new_path': new_path,
                    'category': category,
                    'message': f'File organized into category: {category}'
                }
            
            elif organization_type == 'date':
                # Get current date
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Create date directory
                base_dir = os.path.dirname(os.path.dirname(file_path))
                date_dir = os.path.join(base_dir, 'Dates', today)
                os.makedirs(date_dir, exist_ok=True)
                
                # Move file to date directory
                new_path = os.path.join(date_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                
                # Update history
                self._update_history_filename(file_path, new_path)
                
                return {
                    'success': True,
                    'new_path': new_path,
                    'date': today,
                    'message': f'File organized by date: {today}'
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown organization type: {organization_type}'
                }
        
        except Exception as e:
            print(f"Error organizing file: {str(e)}")
            return {
                'success': False,
                'message': f'Error organizing file: {str(e)}'
            }
    
    def upload_to_cloud(self, file_path, service='google_drive', credentials=None):
        """Upload a file to cloud storage (Google Drive or Dropbox)"""
        # This is a placeholder implementation
        # A real implementation would use the appropriate API for each service
        
        try:
            # Simulate upload
            print(f"Uploading {file_path} to {service}...")
            time.sleep(2)  # Simulate upload time
            
            return {
                'success': True,
                'service': service,
                'message': f'File uploaded to {service} successfully'
            }
        except Exception as e:
            print(f"Error uploading to cloud: {str(e)}")
            return {
                'success': False,
                'message': f'Error uploading to cloud: {str(e)}'
            }
    
    def download_playlist(self, playlist_url, format_id, resolution, compression, download_dir, cookies_file=None):
        """Download an entire YouTube playlist"""
        try:
            # Extract playlist information
            ydl_opts = {
                'extract_flat': True,
                'skip_download': True,
                'quiet': True,
                'ignoreerrors': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info:
                    return {
                        'success': False,
                        'message': 'Failed to extract playlist information'
                    }
                
                # Get video URLs from playlist
                video_urls = []
                for entry in playlist_info.get('entries', []):
                    if entry and 'url' in entry:
                        video_urls.append(entry['url'])
                
                if not video_urls:
                    return {
                        'success': False,
                        'message': 'No videos found in playlist'
                    }
                
                # Start batch download
                return self.batch_download(
                    video_urls,
                    format_id,
                    resolution,
                    compression,
                    download_dir,
                    cookies_file
                )
        
        except Exception as e:
            print(f"Error downloading playlist: {str(e)}")
            return {
                'success': False,
                'message': f'Error downloading playlist: {str(e)}'
            }
    
    def encrypt_file(self, file_path, password, output_filename=None):
        """Encrypt a downloaded file"""
        try:
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.basename(file_path)
                output_filename = f"{base_name}.enc"
            
            output_path = os.path.join(os.path.dirname(file_path), output_filename)
            
            # Use OpenSSL for encryption (simplified implementation)
            cmd = [
                'openssl', 'enc', '-aes-256-cbc',
                '-salt',
                '-in', file_path,
                '-out', output_path,
                '-k', password
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'File encrypted successfully'
            }
        except Exception as e:
            print(f"Error encrypting file: {str(e)}")
            return {
                'success': False,
                'message': f'Error encrypting file: {str(e)}'
            }
    
    def decrypt_file(self, file_path, password, output_filename=None):
        """Decrypt an encrypted file"""
        try:
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.basename(file_path)
                if base_name.endswith('.enc'):
                    output_filename = base_name[:-4]
                else:
                    output_filename = f"decrypted_{base_name}"
            
            output_path = os.path.join(os.path.dirname(file_path), output_filename)
            
            # Use OpenSSL for decryption (simplified implementation)
            cmd = [
                'openssl', 'enc', '-aes-256-cbc',
                '-d',
                '-in', file_path,
                '-out', output_path,
                '-k', password
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'File decrypted successfully'
            }
        except Exception as e:
            print(f"Error decrypting file: {str(e)}")
            return {
                'success': False,
                'message': f'Error decrypting file: {str(e)}'
            }
    
    def send_notification(self, message, notification_type='console'):
        """Send notification on download completion"""
        try:
            if notification_type == 'console':
                print(f"NOTIFICATION: {message}")
                return {
                    'success': True,
                    'message': 'Notification sent to console'
                }
            elif notification_type == 'desktop':
                # This would use a desktop notification library in a real implementation
                print(f"DESKTOP NOTIFICATION: {message}")
                return {
                    'success': True,
                    'message': 'Desktop notification sent'
                }
            else:
                return {
                    'success': False,
                    'message': f'Unknown notification type: {notification_type}'
                }
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return {
                'success': False,
                'message': f'Error sending notification: {str(e)}'
            }
