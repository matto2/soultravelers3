#!/usr/bin/env python3
import re
import os
import glob
from pathlib import Path

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def find_local_image(r2_filename):
    """
    Find the local equivalent of an R2 image by searching through uploads directory.
    Returns the local path if found, None otherwise.
    """
    # Extract just the filename from R2 URL
    filename = r2_filename.split('/')[-1]
    
    # Remove any query parameters or fragments
    filename = filename.split('?')[0].split('#')[0]
    
    # Search in uploads directory recursively
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        # First try exact match
        for img_path in uploads_dir.rglob(filename):
            if img_path.is_file():
                return str(img_path)
        
        # If no exact match, try to find files that start with the base name
        # (handles cases where local files have size suffixes)
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
                # If no unsized version, return the first match
                return matches[0]
    
    # Also search in uploads-new directory
    uploads_new_dir = Path("uploads-new")
    if uploads_new_dir.exists():
        for img_path in uploads_new_dir.rglob(filename):
            if img_path.is_file():
                return str(img_path)
        
        # Try pattern matching here too
        base_name = filename.split('.')[0]
        extension = filename.split('.')[-1] if '.' in filename else ''
        
        if extension:
            pattern = f"{base_name}*.{extension}"
            matches = []
            for img_path in uploads_new_dir.rglob(pattern):
                if img_path.is_file():
                    matches.append(str(img_path))
            
            if matches:
                # Prefer the largest version (without size suffixes)
                for match in matches:
                    if not any(suffix in match for suffix in ['-150x150', '-300x225', '-500wi', '-pi']):
                        return match
                # If no unsized version, return the first match
                return matches[0]
    
    return None

def fix_image_urls(content):
    """
    Replace broken R2.dev URLs with local image paths.
    """
    # Pattern to match R2.dev URLs in markdown images
    pattern = r'(!\[[^\]]*\]\()' + re.escape(R2_BASE) + r'/([^)]+)(\))'
    
    def replacer(match):
        prefix = match.group(1)  # ![alt](
        r2_url = match.group(2)  # filename
        suffix = match.group(3)  # )
        
        # Try to find local equivalent
        local_path = find_local_image(r2_url)
        
        if local_path:
            # Convert to relative path from src/content
            relative_path = f"../../{local_path}"
            print(f"✅ Found local image: {r2_url} -> {relative_path}")
            return f"{prefix}{relative_path}{suffix}"
        else:
            # If no local image found, keep original URL but log it
            print(f"⚠️  No local image found for: {r2_url}")
            return match.group(0)
    
    return re.sub(pattern, replacer, content)

def fix_linked_images(content):
    """
    Fix linked images where both src and href point to R2 URLs.
    """
    # Pattern for linked images: [![alt](r2-url)](r2-url)
    pattern = r'(\[!\[[^\]]*\]\()' + re.escape(R2_BASE) + r'/([^)]+)(\)\]\()' + re.escape(R2_BASE) + r'/([^)]+)(\))'
    
    def replacer(match):
        prefix = match.group(1)  # [![alt](
        src_r2_url = match.group(2)  # src filename
        middle = match.group(3)  # )](
        href_r2_url = match.group(4)  # href filename
        suffix = match.group(5)  # )
        
        # Find local images for both src and href
        src_local = find_local_image(src_r2_url)
        href_local = find_local_image(href_r2_url)
        
        if src_local and href_local:
            src_relative = f"../../{src_local}"
            href_relative = f"../../{href_local}"
            return f"{prefix}{src_relative}{middle}{href_relative}{suffix}"
        elif src_local:
            # If only src found, use it for both
            src_relative = f"../../{src_local}"
            return f"{prefix}{src_relative}{middle}{src_relative}{suffix}"
        else:
            print(f"⚠️  No local images found for linked image: {src_r2_url} -> {href_r2_url}")
            return match.group(0)
    
    return re.sub(pattern, replacer, content)

def test_specific_files():
    """
    Test the fix on a small subset of files that we know have broken images.
    """
    # Test files with known broken images
    test_files = [
        'src/content/blog/tortosa-tarragona-reus-costa-daurada-gems/index.md',
        'src/content/blog/colliore-france-on-bastille-day-family-travel-pyrennees-catalonia-beautiful-village-on-the-med-sea/index.md'
    ]
    
    files_processed = 0
    files_modified = 0
    images_fixed = 0
    
    for filepath in test_files:
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            
            # Count R2 URLs before fixing
            r2_count_before = len(re.findall(re.escape(R2_BASE), original))
            
            # Apply fixes
            modified = fix_image_urls(original)
            modified = fix_linked_images(modified)
            
            # Count R2 URLs after fixing
            r2_count_after = len(re.findall(re.escape(R2_BASE), modified))
            images_fixed += (r2_count_before - r2_count_after)
            
            print(f"\n📄 Processing: {filepath}")
            print(f"   R2 URLs before: {r2_count_before}")
            print(f"   R2 URLs after: {r2_count_after}")
            print(f"   Images fixed: {r2_count_before - r2_count_after}")
            
            if modified != original:
                # Show a sample of the changes
                print(f"   ✅ Changes detected - would modify file")
                
                # Show first few lines of changes
                original_lines = original.split('\n')
                modified_lines = modified.split('\n')
                
                for i, (orig, mod) in enumerate(zip(original_lines, modified_lines)):
                    if orig != mod and i < 10:  # Show first 10 changes
                        print(f"   Line {i+1}:")
                        print(f"     Before: {orig[:100]}...")
                        print(f"     After:  {mod[:100]}...")
                        print()
            else:
                print(f"   ℹ️  No changes needed")
            
            files_processed += 1
            
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
    
    print(f"\n📊 Test Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Images that would be fixed: {images_fixed}")

if __name__ == '__main__':
    print("🧪 Testing image fix on small subset...")
    print(f"📁 Looking for local images in: uploads/, uploads-new/")
    print(f"🎯 Testing R2.dev URL replacement")
    print()
    
    test_specific_files()
    
    print("\n✨ Test complete!")
