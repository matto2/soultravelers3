#!/usr/bin/env python3
import re
import os
import glob

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_image_links(content):
    """
    Fix markdown image links where both src and href point to sized versions.
    Pattern: [![alt](url-with-size.ext)](same-url-with-size.ext)
    Result: [![alt](url-with-size.ext)](url-without-size.ext)
    """
    # Match image markdown with R2 URLs that have size suffixes in both src and href
    # Handles various size patterns: -150x150, -300x225-1, -1024x768-1, -500wi, -pi
    pattern = r'(\[!\[[^\]]*\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+)(\)\]\()(' + re.escape(R2_BASE) + r'/6a00[a-f0-9]+)(-(?:\d+x\d+(?:-\d+)?|\d+wi|pi))(\.[a-z]+\))'
    
    def replacer(match):
        # Keep size in thumbnail src (groups 1-4), remove from link href (groups 5-8)
        # Check if the hash is the same in both src and href
        src_hash = match.group(2).split('/')[-1]
        href_hash = match.group(6).split('/')[-1]
        src_ext = match.group(4)
        href_ext = match.group(8).rstrip(')')
        
        # Only fix if same image (same hash and extension)
        if src_hash == href_hash and src_ext == href_ext:
            # Return with size in src, without size in href
            return match.group(1) + match.group(2) + match.group(3) + match.group(4) + match.group(5) + match.group(6) + href_ext + ')'
        
        return match.group(0)  # No change if different images
    
    return re.sub(pattern, replacer, content)

def process_files():
    files_modified = 0
    links_fixed = 0
    
    for filepath in glob.glob('src/content/blog/**/index.md', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            
            modified = fix_image_links(original)
            
            if modified != original:
                # Count how many links were fixed in this file
                original_count = len(re.findall(r'\[!\[', original))
                modified_count = len(re.findall(r'\[!\[', modified))
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)
                
                files_modified += 1
                # Estimate links fixed (this is approximate)
                links_in_file = len(re.findall(r'\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)', modified))
                links_fixed += 1
                print(f"Fixed: {filepath}")
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    print(f"\n✓ Modified {files_modified} files")
    print(f"✓ Fixed image links with various size patterns")

if __name__ == '__main__':
    process_files()
