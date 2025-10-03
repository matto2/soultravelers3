#!/usr/bin/env python3
"""
Systematically fix missing images by uploading suffixed versions to R2 without suffixes.
Processes images in chunks to avoid overwhelming the system.
FULL VERSION - processes all images
"""

import os
import subprocess
import sys
from pathlib import Path
import time

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

def process_images_in_chunks(chunk_size=20, delay=3):
    """Process images in chunks with delays"""
    
    # Find all images with size suffixes
    print("Finding images with size suffixes...")
    cmd = [
        "find", "uploads", 
        "-name", "*-500wi.jpg", "-o", 
        "-name", "*-300x225.jpg", "-o", 
        "-name", "*-150x150.jpg"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    all_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    
    print(f"Found {len(all_files)} images to process")
    
    # Process in chunks
    total_processed = 0
    total_uploaded = 0
    total_skipped = 0
    total_errors = 0
    
    for i in range(0, len(all_files), chunk_size):
        chunk = all_files[i:i + chunk_size]
        print(f"\n--- Processing chunk {i//chunk_size + 1}/{(len(all_files) + chunk_size - 1)//chunk_size} ---")
        
        for local_file in chunk:
            if not os.path.exists(local_file):
                continue
                
            remote_name = get_remote_name(local_file)
            total_processed += 1
            
            # Check if already exists
            if check_image_exists(remote_name):
                print(f"[{total_processed}] SKIP: {remote_name} (already exists)")
                total_skipped += 1
                continue
            
            # Upload the image
            print(f"[{total_processed}] Uploading: {remote_name}")
            success, error = run_wrangler_upload(local_file, remote_name)
            
            if success:
                total_uploaded += 1
                print(f"[{total_processed}] ✓ SUCCESS: {remote_name}")
            else:
                total_errors += 1
                print(f"[{total_processed}] ✗ ERROR: {remote_name} - {error}")
        
        # Delay between chunks
        if i + chunk_size < len(all_files):
            print(f"Waiting {delay} seconds before next chunk...")
            time.sleep(delay)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total processed: {total_processed}")
    print(f"Successfully uploaded: {total_uploaded}")
    print(f"Skipped (already exist): {total_skipped}")
    print(f"Errors: {total_errors}")

if __name__ == "__main__":
    print("Starting FULL systematic image fix...")
    print("This will upload ALL images with size suffixes to R2 without suffixes")
    print("Processing in chunks to avoid overwhelming the system")
    print("This may take a while with 30,000+ images...")
    
    # Ask for confirmation
    response = input("Continue with ALL images? (y/N): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)
    
    process_images_in_chunks(chunk_size=20, delay=3)


