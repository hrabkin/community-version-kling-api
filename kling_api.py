#!/usr/bin/env python3
"""
Kling AI API Module

This module provides a Python interface for the Kling AI video generation API.
It supports both text-to-video generation and video extension functionality.
"""

import time
import requests
import os
from pathlib import Path
from generate_jwt import encode_jwt_token

class KlingAPI:
    """
    A client for interacting with the Kling AI video generation API.
    """
    
    def __init__(self, access_key=None, secret_key=None):
        """
        Initialize the Kling API client.
        
        Args:
            access_key (str, optional): Kling access key. If not provided, will use KLING_ACCESS_KEY env var.
            secret_key (str, optional): Kling secret key. If not provided, will use KLING_SECRET env var.
        """
        self.access_key = access_key or os.getenv("KLING_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("KLING_SECRET")
        
        if not self.access_key or not self.secret_key:
            raise ValueError("Access key and secret key must be provided either as parameters or environment variables (KLING_ACCESS_KEY, KLING_SECRET)")
        
        self.base_url = "https://api-singapore.klingai.com/v1"
        self._jwt_token = None
        self._jwt_generated_time = 0
    
    def _get_jwt_token(self):
        """Generate or refresh JWT token if needed."""
        current_time = time.time()
        # Refresh token every 25 minutes (1500 seconds) to be safe
        if not self._jwt_token or (current_time - self._jwt_generated_time) > 1500:
            self._jwt_token = encode_jwt_token(self.access_key, self.secret_key)
            self._jwt_generated_time = current_time
        return self._jwt_token
    
    def _get_headers(self):
        """Get standard headers for API requests."""
        return {
            "Authorization": f"Bearer {self._get_jwt_token()}",
            "Content-Type": "application/json"
        }
    
    def create_video(self, prompt, model_name="kling-v1-6", aspect_ratio="9:16", mode="std", duration="10"):
        """
        Create a video using text-to-video generation.
        
        Args:
            prompt (str): Text prompt for video generation (max 2500 characters)
            model_name (str): Model name (default: "kling-v1-6")
            aspect_ratio (str): Aspect ratio (default: "9:16")
            mode (str): Generation mode (default: "std")
            duration (str): Video duration in seconds (default: "10")
            
        Returns:
            dict: API response containing task_id and status
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If prompt exceeds character limit
        """
        if len(prompt) > 2500:
            raise ValueError(f"Prompt length ({len(prompt)}) exceeds 2500 character limit")
        
        url = f"{self.base_url}/videos/text2video"
        
        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "duration": duration
        }
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Video creation failed: {e}"
            
            # Try to get detailed error from response
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    if 'message' in error_details:
                        error_msg = f"Video creation failed: {error_details['message']}"
                    elif 'error' in error_details:
                        error_msg = f"Video creation failed: {error_details['error']}"
                    else:
                        error_msg = f"Video creation failed: {error_details}"
                except:
                    # If response is not JSON, use text
                    error_msg = f"Video creation failed: {e.response.text}"
                
                # Add status code and URL for debugging
                error_msg += f" (Status: {e.response.status_code}, URL: {url})"
                
            raise requests.exceptions.RequestException(error_msg) from e
    
    def extend_video(self, video_id, prompt=None):
        """
        Extend an existing video.
        
        Args:
            video_id (str): ID of the video to extend
            prompt (str, optional): Text prompt for extension (max 2500 characters)
            
        Returns:
            dict: API response containing task_id and status
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If prompt exceeds character limit
        """
        if prompt and len(prompt) > 2500:
            raise ValueError(f"Prompt length ({len(prompt)}) exceeds 2500 character limit")
        
        url = f"{self.base_url}/videos/video-extend"
        
        payload = {"video_id": video_id}
        if prompt:
            payload["prompt"] = prompt
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Video extension failed: {e}"
            
            # Try to get detailed error from response
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    if 'message' in error_details:
                        error_msg = f"Video extension failed: {error_details['message']}"
                    elif 'error' in error_details:
                        error_msg = f"Video extension failed: {error_details['error']}"
                    else:
                        error_msg = f"Video extension failed: {error_details}"
                except:
                    # If response is not JSON, use text
                    error_msg = f"Video extension failed: {e.response.text}"
                
                # Add status code and URL for debugging
                error_msg += f" (Status: {e.response.status_code}, URL: {url})"
                
            raise requests.exceptions.RequestException(error_msg) from e
    
    def check_status(self, task_id, operation="creation"):
        """
        Check the status of a video generation or extension task.
        
        Args:
            task_id (str): Task ID to check
            operation (str): Type of operation ("creation" or "extension")
            
        Returns:
            dict: API response with task status, or None if request failed
        """
        if operation == "extension":
            url = f"{self.base_url}/videos/video-extend/{task_id}"
        else:
            url = f"{self.base_url}/videos/text2video/{task_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def monitor_task(self, task_id, operation="creation", check_interval=5, max_wait_time=1800, verbose=True):
        """
        Monitor a video generation or extension task until completion.
        
        Args:
            task_id (str): Task ID to monitor
            operation (str): Type of operation ("creation" or "extension")
            check_interval (int): Seconds between status checks (default: 5)
            max_wait_time (int): Maximum time to wait in seconds (default: 1800)
            verbose (bool): Whether to print status updates (default: True)
            
        Returns:
            list: List of generated videos, or None if failed/timeout
        """
        if verbose:
            print(f"Monitoring task {task_id}...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_response = self.check_status(task_id, operation)
            
            if not status_response:
                if verbose:
                    print("Failed to check status. Retrying in 5 seconds...")
                time.sleep(check_interval)
                continue
            
            if status_response.get('code') != 0:
                if verbose:
                    print(f"API Error: {status_response.get('message', 'Unknown error')}")
                return None
            
            data = status_response.get('data', {})
            task_status = data.get('task_status', '')
            task_status_msg = data.get('task_status_msg', '')
            
            if verbose:
                print(f"Status: {task_status}")
                if task_status_msg:
                    print(f"Message: {task_status_msg}")
            
            if task_status == 'succeed':
                task_result = data.get('task_result', {})
                videos = task_result.get('videos', [])
                
                if verbose:
                    if videos:
                        print(f"\n✅ Video {operation} completed!")
                        for i, video in enumerate(videos):
                            print(f"Video {i+1}:")
                            print(f"  ID: {video.get('id', 'N/A')}")
                            print(f"  URL: {video.get('url', 'N/A')}")
                            print(f"  Duration: {video.get('duration', 'N/A')} seconds")
                    else:
                        print(f"Video {operation} completed but no videos found in response.")
                
                return videos
                
            elif task_status == 'failed':
                if verbose:
                    print(f"❌ Video {operation} failed: {task_status_msg}")
                return None
                
            elif task_status in ['submitted', 'processing']:
                if verbose:
                    print(f"⏳ Still {task_status}... Checking again in {check_interval} seconds")
                time.sleep(check_interval)
            else:
                if verbose:
                    print(f"Unknown status: {task_status}")
                time.sleep(check_interval)
        
        if verbose:
            print(f"⏰ Timeout after {max_wait_time} seconds")
        return None
    
    def download_video(self, url, filename, results_dir="videos"):
        """
        Download a video from URL to local storage.
        
        Args:
            url (str): Video URL to download
            filename (str): Local filename to save as
            results_dir (str): Directory to save videos (default: "video")
            
        Returns:
            str: Path to downloaded file, or None if download failed
        """
        video_path = Path(results_dir)
        video_path.mkdir(exist_ok=True)
        
        file_path = video_path / filename
        
        try:
            print(f"📥 Downloading video to {file_path}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Video downloaded successfully: {file_path}")
            return str(file_path)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading video: {e}")
            return None
    
    def check_and_download(self, task_id, operation="creation", download=True, filename_prefix=None, results_dir="videos"):
        """
        Check task status and optionally download completed videos.
        
        Args:
            task_id (str): Task ID to check
            operation (str): Type of operation ("creation" or "extension")
            download (bool): Whether to download videos if ready (default: True)
            filename_prefix (str, optional): Prefix for downloaded filenames
            results_dir (str): Directory to save videos (default: "video")
            
        Returns:
            dict: Status information with keys:
                - status: current task status
                - message: status message if any
                - videos: list of video info if completed
                - downloaded_files: list of downloaded file paths if download=True
        """
        result = {
            'status': None,
            'message': None,
            'videos': [],
            'downloaded_files': []
        }
        
        status_response = self.check_status(task_id, operation)
        
        if not status_response:
            result['status'] = 'error'
            result['message'] = 'Failed to check status'
            return result
        
        if status_response.get('code') != 0:
            result['status'] = 'error'
            result['message'] = status_response.get('message', 'Unknown API error')
            return result
        
        data = status_response.get('data', {})
        task_status = data.get('task_status', '')
        task_status_msg = data.get('task_status_msg', '')
        
        result['status'] = task_status
        result['message'] = task_status_msg
        
        print(f"📋 Task {task_id} status: {task_status}")
        if task_status_msg:
            print(f"📋 Message: {task_status_msg}")
        
        if task_status == 'succeed':
            task_result = data.get('task_result', {})
            videos = task_result.get('videos', [])
            result['videos'] = videos
            
            if videos:
                print(f"\n✅ Found {len(videos)} completed video(s)!")
                for i, video in enumerate(videos):
                    print(f"Video {i+1}:")
                    print(f"  ID: {video.get('id', 'N/A')}")
                    print(f"  URL: {video.get('url', 'N/A')}")
                    print(f"  Duration: {video.get('duration', 'N/A')} seconds")
                
                if download:
                    print(f"\n📥 Downloading videos...")
                    for i, video in enumerate(videos):
                        video_url = video.get('url')
                        video_id = video.get('id', f'video_{i+1}')
                        
                        if video_url:
                            # Generate filename
                            if filename_prefix:
                                if len(videos) > 1:
                                    filename = f"{filename_prefix}_{i+1}.mp4"
                                else:
                                    filename = f"{filename_prefix}.mp4"
                            else:
                                filename = f"{video_id}_.mp4"
                            
                            downloaded_path = self.download_video(video_url, filename, results_dir)
                            if downloaded_path:
                                result['downloaded_files'].append(downloaded_path)
            else:
                print("✅ Task completed but no videos found in response.")
                
        elif task_status == 'failed':
            print(f"❌ Task failed: {task_status_msg}")
            
        elif task_status in ['submitted', 'processing']:
            print(f"⏳ Task is still {task_status}...")
            
        return result