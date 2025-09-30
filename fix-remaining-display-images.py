#!/usr/bin/env python3
import re
import os
import glob

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_image_src(content):
    """
    Remove size suffixes from image src, handling both linked and standalone images.
    """
    
    # Fix linked images: [![alt](sized-image)](any-image) - using DOTALL for multiline
    pattern1 = r'(\[!\[[^\]]*\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+)(\s+"[^"]*")?\]\('
    
    def replacer1(match):
        # Rebuild without the size suffix in src
        return match.group(1) + match.group(2) + match.group(4) + (match.group(5) or '') + ']('
    
    content = re.sub(pattern1, replacer1, content, flags=re.DOTALL)
    
    # Fix standalone images: ![alt](sized-image) - NOT followed by ]( 
    pattern2 = r'(!\[[^\]]*\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+)(\s+"[^"]*")?\)(?!\])'
    
    def replacer2(match):
        # Rebuild without the size suffix
        return match.group(1) + match.group(2) + match.group(4) + (match.group(5) or '') + ')'
    
    content = re.sub(pattern2, replacer2, content, flags=re.DOTALL)
    
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
    print(f"✓ All image src attributes now point to full-size images")

if __name__ == '__main__':
    process_files()
