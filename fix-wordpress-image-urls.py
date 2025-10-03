#!/usr/bin/env python3
"""
Fix WordPress image URLs in blog posts.
Replace old soultravelers3new.local URLs with R2 URLs.
"""

import os
import re
import glob

def fix_wordpress_urls(content):
    """Replace WordPress URLs with R2 URLs"""
    
    # Pattern 1: [![alt](http://soultravelers3new.local/path)](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    # Replace with: ![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    pattern1 = r'\[!\[([^\]]*)\]\(http://soultravelers3new\.local/[^)]+\)\]\((https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev/[^)]+)\)'
    content = re.sub(pattern1, r'![\1](\2)', content)
    
    # Pattern 2: ![alt](http://soultravelers3new.local/path) - standalone images
    # Replace with: ![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    pattern2 = r'!\[([^\]]*)\]\(http://soultravelers3new\.local/([^)]+)\)'
    content = re.sub(pattern2, r'![\1](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/\2)', content)
    
    # Pattern 3: [![alt](http://soultravelers3new.local/path)](http://soultravelers3new.local/path) - linked images
    # Replace with: ![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    pattern3 = r'\[!\[([^\]]*)\]\(http://soultravelers3new\.local/([^)]+)\)\]\(http://soultravelers3new\.local/[^)]+\)'
    content = re.sub(pattern3, r'![\1](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/\2)', content)
    
    # Pattern 4: [![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)](http://soultravelers3new.local/path) - R2 image with WordPress link
    # Replace with: ![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    pattern4 = r'\[!\[([^\]]*)\]\((https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev/[^)]+)\)\]\(http://soultravelers3new\.local/[^)]+\)'
    content = re.sub(pattern4, r'![\1](\2)', content)
    
    # Pattern 5: [![alt](http://soultravelers3new.local/path)](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path) - already has R2 link
    # Replace with: ![alt](https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/path)
    pattern5 = r'\[!\[([^\]]*)\]\(http://soultravelers3new\.local/[^)]+\)\]\((https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev/[^)]+)\)'
    content = re.sub(pattern5, r'![\1](\2)', content)
    
    return content

def process_files():
    """Process all blog markdown files"""
    files_modified = 0
    
    for filepath in glob.glob('src/content/blog/**/index.md', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            
            modified = fix_wordpress_urls(original)
            
            if modified != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)
                
                files_modified += 1
                print(f"Fixed: {filepath}")
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    print(f"\n✓ Modified {files_modified} files")
    print(f"✓ All WordPress image URLs now point to R2")

if __name__ == '__main__':
    print("🔧 Fixing WordPress image URLs...")
    print("This will replace old soultravelers3new.local URLs with R2 URLs")
    
    process_files()
