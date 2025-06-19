#!/usr/bin/env python3
import argparse
import json
import sys
import os
from pathlib import Path
from kling_api import KlingAPI

def load_prompts(json_file):
    """Load prompts from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file}'.")
        sys.exit(1)

def get_selected_prompts(prompts, indices):
    """Get prompts by indices and concatenate them"""
    selected_prompts = []
    
    for idx in indices:
        if 0 <= idx < len(prompts):
            prompt_text = prompts[idx].get('prompt', '')
            if prompt_text:
                selected_prompts.append(prompt_text)
        else:
            print(f"Warning: Index {idx} is out of range. Skipping.")
    
    return " ".join(selected_prompts)



def get_filename_from_prompt_and_indices(prompt_file, indices):
    """Generate filename based on prompt file name and indices"""
    # Get the base name without extension
    base_name = Path(prompt_file).stem
    
    # Create indices string
    indices_str = "_".join(map(str, indices))
    
    # Combine with .mp4 extension
    return f"{base_name}_{indices_str}.mp4"



def main():
    parser = argparse.ArgumentParser(description='Generate or extend video using Kling API')
    parser.add_argument('--extend', metavar='VIDEO_ID', help='Extend existing video by providing video ID')
    parser.add_argument('prompt', nargs='?', help='Path to the JSON file containing prompts (required for new video generation)')
    parser.add_argument('indices', nargs='?', help='Comma-separated indices to select from the prompt list (e.g., 1,2,3) (required for new video generation)')
    parser.add_argument('--model', default='kling-v2-master', help='Model name (default: kling-v2-master)')
    parser.add_argument('--aspect-ratio', default='9:16', help='Aspect ratio (default: 9:16)')
    parser.add_argument('--mode', default='std', help='Generation mode std/pro (default: std)')
    parser.add_argument('--duration', default='10', help='Video duration (default: 10)')
    parser.add_argument('--no-monitor', action='store_true', help='Don\'t monitor video generation status')
    
    args = parser.parse_args()
    
    # Check if extending video or creating new one
    if args.extend:
        # Video extension mode
        video_id = args.extend
        concatenated_prompt = None
        
        # If prompts are provided for extension
        if args.prompt and args.indices:
            try:
                indices = [int(i.strip()) for i in args.indices.split(',')]
            except ValueError:
                print("Error: Indices must be comma-separated integers (e.g., 1,2,3)")
                sys.exit(1)
            
            # Load prompts
            prompts = load_prompts(args.prompt)
            print(f"Loaded {len(prompts)} prompts from {args.prompt}")
            
            # Get selected prompts
            concatenated_prompt = get_selected_prompts(prompts, indices)
            
            if concatenated_prompt:
                # Check prompt length limit
                if len(concatenated_prompt) > 2500:
                    print(f"❌ Error: Concatenated prompt is {len(concatenated_prompt)} characters, which exceeds the 2500 character limit.")
                    print("Please select fewer prompts or use shorter prompts.")
                    sys.exit(1)
                
                print(f"Selected indices: {indices}")
                print(f"Concatenated prompt length: {len(concatenated_prompt)} characters")
                print(f"Prompt preview: {concatenated_prompt[:200]}...")
        
        print(f"Extending video with ID: {video_id}")
        if concatenated_prompt:
            print(f"Using prompt for extension")
        else:
            print("Extending video without additional prompt")
            
        # Initialize API client
        try:
            api = KlingAPI()
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        # Extend video
        print("Extending video...")
        try:
            response = api.extend_video(video_id=video_id, prompt=concatenated_prompt)
        except Exception as e:
            print(f"Error extending video: {e}")
            sys.exit(1)
        
        operation = "extension"
        filename_base = f"extended_{video_id}"
        if args.prompt and args.indices:
            filename_base += f"_{Path(args.prompt).stem}_{'_'.join(map(str, indices))}"
        filename = f"{filename_base}.mp4"
        
    else:
        # Video creation mode
        if not args.prompt or not args.indices:
            print("Error: For new video generation, both 'prompt' and 'indices' arguments are required.")
            print("Use --help for usage information.")
            sys.exit(1)
        
        # Parse indices
        try:
            indices = [int(i.strip()) for i in args.indices.split(',')]
        except ValueError:
            print("Error: Indices must be comma-separated integers (e.g., 1,2,3)")
            sys.exit(1)
        
        # Load prompts
        prompts = load_prompts(args.prompt)
        print(f"Loaded {len(prompts)} prompts from {args.prompt}")
        
        # Get selected prompts
        concatenated_prompt = get_selected_prompts(prompts, indices)
        
        if not concatenated_prompt:
            print("Error: No valid prompts selected.")
            sys.exit(1)
        
        # Check prompt length limit
        if len(concatenated_prompt) > 2500:
            print(f"❌ Error: Concatenated prompt is {len(concatenated_prompt)} characters, which exceeds the 2500 character limit.")
            print("Please select fewer prompts or use shorter prompts.")
            sys.exit(1)
        
        print(f"Selected indices: {indices}")
        print(f"Concatenated prompt length: {len(concatenated_prompt)} characters")
        print(f"Prompt preview: {concatenated_prompt[:200]}...")
        
        # Initialize API client
        try:
            api = KlingAPI()
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        # Create video
        print("Creating video...")
        try:
            response = api.create_video(
                prompt=concatenated_prompt,
                model_name=args.model,
                aspect_ratio=args.aspect_ratio,
                mode=args.mode,
                duration=args.duration
            )
        except Exception as e:
            print(f"Error creating video: {e}")
            sys.exit(1)
        
        operation = "creation"
        filename = get_filename_from_prompt_and_indices(args.prompt, indices)
    
    if response.get('code') != 0:
        print(f"❌ Video {operation} failed: {response.get('message', 'Unknown error')}")
        sys.exit(1)
    
    data = response.get('data', {})
    task_id = data.get('task_id')
    
    if not task_id:
        print("❌ No task ID received from API")
        sys.exit(1)
    
    print(f"✅ Video {operation} submitted successfully!")
    print(f"Task ID: {task_id}")
    print(f"Status: {data.get('task_status', 'Unknown')}")
    
    if not args.no_monitor:
        videos = api.monitor_task(task_id, operation)
        if videos:
            print(f"\n🎬 {operation.capitalize()}ed {len(videos)} video(s) successfully!")
            
            # Download videos
            for i, video in enumerate(videos):
                video_url = video.get('url')
                if video_url:
                    if len(videos) > 1:
                        # If multiple videos, add index to filename
                        base_name = Path(filename).stem
                        extension = Path(filename).suffix
                        download_filename = f"{base_name}_{i+1}{extension}"
                    else:
                        download_filename = filename
                    
                    downloaded_path = api.download_video(video_url, download_filename)
                    if downloaded_path:
                        print(f"🎬 Video saved: {downloaded_path}")
        else:
            print(f"\n❌ Video {operation} was not successful")
    else:
        print(f"\nTo check status later, use task ID: {task_id}")

if __name__ == "__main__":
    main() 