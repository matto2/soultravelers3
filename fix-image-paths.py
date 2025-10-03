#!/usr/bin/env python3
import re
import os
import glob
from pathlib import Path

def fix_image_paths():
    """
    Fix incorrect image paths that have double uploads directories
    """
    content_dir = Path("src/content")
    if not content_dir.exists():
        print("❌ src/content directory not found")
        return
    
    # Pattern to match incorrect paths like ../../uploads/uploads-new/ or ../../uploads/uploads/
    incorrect_pattern = r'\.\./\.\./uploads/uploads(?:-new)?/'
    correct_replacement = '../../uploads/'
    
    files_processed = 0
    files_modified = 0
    total_replacements = 0
    
    print("🔧 Fixing incorrect image paths...")
    
    # Process all markdown files
    for md_file in content_dir.rglob("*.md"):
        files_processed += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix the incorrect paths
            content = re.sub(incorrect_pattern, correct_replacement, content)
            
            if content != original_content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_modified += 1
                replacements = len(re.findall(incorrect_pattern, original_content))
                total_replacements += replacements
                print(f"✅ Fixed {replacements} paths in {md_file}")
        
        except Exception as e:
            print(f"❌ Error processing {md_file}: {e}")
    
    print(f"\n🎉 Path fixing complete!")
    print(f"📊 Files processed: {files_processed}")
    print(f"📊 Files modified: {files_modified}")
    print(f"📊 Total path corrections: {total_replacements}")

if __name__ == "__main__":
    fix_image_paths()
