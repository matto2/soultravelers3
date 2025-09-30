#!/usr/bin/env python3
import re
import os
import glob

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_image_src(content):
    """
    Remove size suffixes from image src in markdown so full images display.
    Pattern: [![alt](url-with-size.ext)](url-with-or-without-size.ext)
    Result: [![alt](url-without-size.ext)](url-with-or-without-size.ext)
    OR: ![alt](url-with-size.ext)
    Result: ![alt](url-without-size.ext)
    """
    
    # Fix linked images: [![alt](sized-image)](any-image)
    # Change to: [![alt](full-image)](any-image)
    pattern1 = r'(\[!\[[^\]]*\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+\)\]\([^)]+\))'
    content = re.sub(pattern1, r'\1\2\4', content)
    
    # Fix standalone images: ![alt](sized-image)
    # Change to: ![alt](full-image)
    pattern2 = r'(!\[[^\]]*\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+\))'
    content = re.sub(pattern2, r'\1\2\4', content)
    
    return content

def process_files():
    files_modified = 0
    
    for filepath in glob.glob('src/content/blog/**/index.md', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            
            modified = fix_image_src(original)
            
            if modified != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)
                
                files_modified += 1
                print(f"Fixed: {filepath}")
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    print(f"\n✓ Modified {files_modified} files")
    print(f"✓ All images now display full-size")

if __name__ == '__main__':
    process_files()
