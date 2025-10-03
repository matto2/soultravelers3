#!/usr/bin/env python3
import re
import os
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def check_r2_image_exists(r2_url):
    """Check if an R2 image exists by making a HEAD request"""
    try:
        response = requests.head(r2_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def find_local_image(r2_filename):
    """
    Find the local equivalent of an R2 image by searching through uploads directory.
    Returns the local path if found, None otherwise.
    """
    # Extract just the filename from R2 URL
    filename = r2_filename.split('/')[-1]
    filename = filename.split('?')[0].split('#')[0]
    
    # Search in uploads directory recursively
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        base_name = filename.split('.')[0]
        extension = filename.split('.')[-1] if '.' in filename else ''
        
        if extension:
            pattern = f"{base_name}*.{extension}"
            matches = []
            for img_path in uploads_dir.rglob(pattern):
                if img_path.is_file():
                    matches.append(str(img_path))
            
            if matches:
                # Prefer the largest version (without size suffixes)
                for match in matches:
                    if not any(suffix in match for suffix in ['-150x150', '-300x225', '-500wi', '-pi']):
                        return match
                # If no unsized version, return any match
                return matches[0]
    
    return None

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match R2 URLs in markdown images
        pattern = r'(!\[[^\]]*\]\()' + re.escape(R2_BASE) + r'/([^)]+)(\))'
        
        def replace_image(match):
            prefix = match.group(1)
            r2_url = match.group(2)
            suffix = match.group(3)
            
            # Check if R2 image exists
            full_r2_url = f"{R2_BASE}/{r2_url}"
            if check_r2_image_exists(full_r2_url):
                return match.group(0)  # Keep original if R2 image exists
            
            # Try to find local equivalent
            local_path = find_local_image(r2_url)
            
            if local_path:
                # Convert to relative path from src/content
                relative_path = f"../../{local_path}"
                print(f"✅ Replacing missing R2 image: {r2_url} -> {relative_path}")
                return f"{prefix}{relative_path}{suffix}"
            else:
                print(f"⚠️  No local image found for: {r2_url}")
                return match.group(0)  # Keep original if no local image found
        
        # Replace all R2 URLs that don't exist
        content = re.sub(pattern, replace_image, content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all markdown files"""
    content_dir = Path("src/content")
    if not content_dir.exists():
        print("❌ src/content directory not found")
        return
    
    print("🔍 Finding all markdown files...")
    md_files = list(content_dir.rglob("*.md"))
    print(f"📁 Found {len(md_files)} markdown files")
    
    print("🔧 Processing files to replace missing R2 images with local equivalents...")
    
    files_processed = 0
    files_modified = 0
    
    # Process files in batches to avoid overwhelming the server
    batch_size = 10
    for i in range(0, len(md_files), batch_size):
        batch = md_files[i:i + batch_size]
        print(f"📦 Processing batch {i//batch_size + 1}/{(len(md_files) + batch_size - 1)//batch_size}")
        
        for file_path in batch:
            files_processed += 1
            if process_file(file_path):
                files_modified += 1
        
        # Small delay between batches to be respectful to R2
        if i + batch_size < len(md_files):
            time.sleep(0.5)
    
    print(f"\n🎉 Processing complete!")
    print(f"📊 Files processed: {files_processed}")
    print(f"📊 Files modified: {files_modified}")

if __name__ == "__main__":
    main()
