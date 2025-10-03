#!/usr/bin/env python3
import re
import os
import subprocess
from pathlib import Path

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def check_r2_image_exists(r2_url):
    """Check if an R2 image exists using curl"""
    try:
        result = subprocess.run(['curl', '-I', r2_url], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and '200 OK' in result.stdout
    except:
        return False

def find_local_image(r2_filename):
    """Find the local equivalent of an R2 image"""
    filename = r2_filename.split('/')[-1]
    filename = filename.split('?')[0].split('#')[0]
    
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
                return matches[0]
    
    return None

def main():
    """Identify missing R2 images and their local equivalents"""
    content_dir = Path("src/content")
    if not content_dir.exists():
        print("❌ src/content directory not found")
        return
    
    print("🔍 Scanning for R2 image references...")
    
    missing_images = []
    existing_images = []
    
    # Find all R2 URLs in markdown files
    pattern = re.escape(R2_BASE) + r'/([^)\s]+)'
    
    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            matches = re.findall(pattern, content)
            for r2_url in matches:
                full_r2_url = f"{R2_BASE}/{r2_url}"
                
                if check_r2_image_exists(full_r2_url):
                    existing_images.append(r2_url)
                else:
                    # Check if local equivalent exists
                    local_path = find_local_image(r2_url)
                    if local_path:
                        missing_images.append({
                            'r2_url': r2_url,
                            'local_path': local_path,
                            'file': str(md_file)
                        })
                    else:
                        print(f"⚠️  No local equivalent found for: {r2_url}")
        
        except Exception as e:
            print(f"❌ Error processing {md_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Existing R2 images: {len(existing_images)}")
    print(f"❌ Missing R2 images with local equivalents: {len(missing_images)}")
    
    if missing_images:
        print(f"\n📋 Missing images that need to be uploaded to R2:")
        print("=" * 80)
        
        # Group by unique R2 URL to avoid duplicates
        unique_missing = {}
        for item in missing_images:
            r2_url = item['r2_url']
            if r2_url not in unique_missing:
                unique_missing[r2_url] = item
        
        for r2_url, item in unique_missing.items():
            print(f"R2 URL: {r2_url}")
            print(f"Local file: {item['local_path']}")
            print(f"Found in: {item['file']}")
            print("-" * 40)
        
        # Create upload script
        print(f"\n📝 Creating upload script...")
        with open("upload-missing-images.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Script to upload missing images to R2\n")
            f.write("# You'll need to configure your R2 credentials first\n\n")
            
            for r2_url, item in unique_missing.items():
                local_file = item['local_path']
                f.write(f"# Upload {r2_url}\n")
                f.write(f"# aws s3 cp \"{local_file}\" \"s3://your-r2-bucket/{r2_url}\"\n")
                f.write(f"echo \"Uploading {r2_url}...\"\n\n")
        
        print(f"✅ Created upload-missing-images.sh with {len(unique_missing)} images to upload")
        print(f"📁 Edit the script to add your R2 bucket name and credentials")

if __name__ == "__main__":
    main()
