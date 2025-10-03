#!/usr/bin/env python3
"""
Test script to fix a small batch of images first
"""

import os
import subprocess
import sys
from pathlib import Path

def run_wrangler_upload(local_file, remote_name):
    """Upload a file to R2 using wrangler with --remote flag"""
    try:
        cmd = [
            "wrangler", "r2", "object", "put", 
            f"matts-media/{remote_name}", 
            f"--file={local_file}", 
            "--remote"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def get_remote_name(local_path):
    """Extract the remote name by removing size suffixes"""
    filename = os.path.basename(local_path)
    
    # Remove common size suffixes
    suffixes_to_remove = [
        '-500wi-300x225.jpg',
        '-500wi-150x150.jpg', 
        '-500wi.jpg',
        '-300x225.jpg',
        '-150x150.jpg',
        '-scaled-150x150.jpg',
        '-scaled-300x225.jpg'
    ]
    
    for suffix in suffixes_to_remove:
        if filename.endswith(suffix):
            return filename[:-len(suffix)] + '.jpg'
    
    return filename

def check_image_exists(remote_name):
    """Check if image already exists in R2"""
    try:
        cmd = ["curl", "-I", f"https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/{remote_name}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return "200 OK" in result.stdout
    except:
        return False

def main():
    print("Testing image fix with first 10 images...")
    
    # Find first 10 images with size suffixes
    cmd = [
        "find", "uploads", 
        "-name", "*-500wi.jpg", "-o", 
        "-name", "*-300x225.jpg", "-o", 
        "-name", "*-150x150.jpg"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    all_files = [f.strip() for f in result.stdout.split('\n') if f.strip()][:10]
    
    print(f"Testing with {len(all_files)} images")
    
    for i, local_file in enumerate(all_files, 1):
        if not os.path.exists(local_file):
            print(f"[{i}] SKIP: {local_file} (file not found)")
            continue
            
        remote_name = get_remote_name(local_file)
        
        # Check if already exists
        if check_image_exists(remote_name):
            print(f"[{i}] SKIP: {remote_name} (already exists)")
            continue
        
        # Upload the image
        print(f"[{i}] Uploading: {remote_name}")
        success, error = run_wrangler_upload(local_file, remote_name)
        
        if success:
            print(f"[{i}] ✓ SUCCESS: {remote_name}")
        else:
            print(f"[{i}] ✗ ERROR: {remote_name} - {error}")

if __name__ == "__main__":
    main()


