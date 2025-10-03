#!/usr/bin/env python3
"""
Comprehensive image fix script for SoulTravelers3
Fixes ALL broken image references to use R2 store
"""

import os
import re
import glob
from pathlib import Path
import shutil
from datetime import datetime

# R2 store base URL
R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def backup_files():
    """Create a backup of all markdown files"""
    backup_dir = Path("backup_markdown") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    content_dirs = ["src/content/blog", "src/content/drafts"]

    for content_dir in content_dirs:
        if Path(content_dir).exists():
            dest_dir = backup_dir / content_dir
            shutil.copytree(content_dir, dest_dir)

    print(f"✅ Backup created at: {backup_dir}\n")
    return backup_dir

def fix_soultravelers_local_urls(content):
    """Fix soultravelers3new.local URLs to use R2"""
    changes = 0

    # Pattern 1: http://soultravelers3new.local/images/...
    new_content = re.sub(
        r'http://soultravelers3new\.local/images/',
        f'{R2_BASE}/',
        content
    )
    changes += len(re.findall(r'http://soultravelers3new\.local/images/', content))

    # Pattern 2: http://soultravelers3new.local/wp-content/uploads/...
    new_content = re.sub(
        r'http://soultravelers3new\.local/wp-content/uploads/',
        f'{R2_BASE}/',
        new_content
    )
    changes += len(re.findall(r'http://soultravelers3new\.local/wp-content/uploads/', content))

    # Pattern 3: Any other soultravelers3new.local references
    new_content = re.sub(
        r'http://soultravelers3new\.local/',
        f'{R2_BASE}/',
        new_content
    )
    changes += len(re.findall(r'http://soultravelers3new\.local/', content))

    return new_content, changes

def remove_zemanta_sections(content):
    """Remove Zemanta related articles sections"""
    changes = 0

    # Count Zemanta references before removal
    changes = len(re.findall(r'http://i\.zemanta\.com/', content))

    # Remove individual Zemanta image links
    # Pattern: [![](http://i.zemanta.com/...)...]...[text](url)
    new_content = re.sub(
        r'\[!\[\]\(http://i\.zemanta\.com/[^\]]+\)\]\([^\)]+\)\[([^\]]+)\]\([^\)]+\)\s*',
        '',
        content
    )

    # Remove any remaining zemanta references
    new_content = re.sub(
        r'!\[\]\(http://i\.zemanta\.com/[^\)]+\)',
        '',
        new_content
    )

    return new_content, changes

def fix_typepad_urls(content):
    """Fix Typepad image URLs to use R2"""
    changes = 0

    def replace_typepad(match):
        nonlocal changes
        changes += 1
        image_id = match.group(1)
        # Construct R2 URL from image ID
        return f'{R2_BASE}/{image_id}.jpg'

    new_content = re.sub(
        r'https?://soultravelers3\.typepad\.com/\.a/([a-f0-9]+)(?:-[0-9]+wi)?',
        replace_typepad,
        content
    )

    return new_content, changes

def remove_facebook_cdn_refs(content):
    """Remove Facebook CDN image references"""
    changes = len(re.findall(r'!\[[^\]]*\]\(https?://[^)]*fbcdn[^)]*\)', content))

    new_content = re.sub(
        r'!\[[^\]]*\]\(https?://[^)]*fbcdn[^)]*\)',
        '',
        content
    )

    return new_content, changes

def fix_duplicate_wp_content_paths(content):
    """Fix duplicate wp-content/uploads paths"""
    changes = 0

    # Fix /wp-content/uploads/wp-content/uploads/ -> /wp-content/uploads/
    changes += len(re.findall(r'/wp-content/uploads/wp-content/uploads/', content))
    new_content = re.sub(
        r'/wp-content/uploads/wp-content/uploads/',
        '/wp-content/uploads/',
        content
    )

    # Also fix in R2 URLs if they exist
    changes += len(re.findall(r'https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev/wp-content/uploads/', content))
    new_content = re.sub(
        r'https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev/wp-content/uploads/',
        f'{R2_BASE}/',
        new_content
    )

    return new_content, changes

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        total_changes = 0

        # Apply all fixes
        content, changes = fix_soultravelers_local_urls(content)
        total_changes += changes

        content, changes = remove_zemanta_sections(content)
        total_changes += changes

        content, changes = fix_typepad_urls(content)
        total_changes += changes

        content, changes = remove_facebook_cdn_refs(content)
        total_changes += changes

        content, changes = fix_duplicate_wp_content_paths(content)
        total_changes += changes

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, total_changes, file_path

        return False, 0, None

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0, None

def find_markdown_files():
    """Find all markdown files in content directories"""
    markdown_files = []

    for filepath in glob.glob('src/content/blog/**/index.md', recursive=True):
        markdown_files.append(filepath)

    for filepath in glob.glob('src/content/drafts/**/index.md', recursive=True):
        markdown_files.append(filepath)

    return markdown_files

def main():
    print("🚀 Starting comprehensive image fix...")
    print(f"🎯 Target: Convert ALL images to use R2 store")
    print(f"📦 R2 Store: {R2_BASE}\n")

    # Create backup first
    backup_dir = backup_files()

    # Find all markdown files
    markdown_files = find_markdown_files()
    print(f"Found {len(markdown_files)} markdown files\n")

    # Process all files
    fixed_count = 0
    total_changes = 0
    fixed_files = []

    for i, file_path in enumerate(markdown_files, 1):
        if i % 100 == 0:
            print(f"Processing {i}/{len(markdown_files)}...")

        changed, changes, fixed_file = process_file(file_path)
        if changed:
            fixed_count += 1
            total_changes += changes
            fixed_files.append((fixed_file, changes))

    print(f"\n✅ COMPLETE!\n")
    print(f"📊 SUMMARY:")
    print(f"   Files processed: {len(markdown_files)}")
    print(f"   Files modified: {fixed_count}")
    print(f"   Total changes made: {total_changes}")
    print(f"   Backup location: {backup_dir}\n")

    if fixed_files:
        print(f"Top 10 files with most changes:")
        sorted_files = sorted(fixed_files, key=lambda x: x[1], reverse=True)[:10]
        for f, changes in sorted_files:
            print(f"  - {f} ({changes} changes)")

        if len(fixed_files) > 10:
            print(f"  ... and {len(fixed_files) - 10} more files\n")

    # Count remaining broken images
    print("🔍 Checking for remaining broken images...")
    remaining_broken = 0
    for filepath in markdown_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for any non-R2 image URLs
                remaining_broken += len(re.findall(r'!\[[^\]]*\]\((?!https://pub-ac94b3f306b24c0dba4238943c97f2e1\.r2\.dev)[^)]+\)', content))
        except:
            pass

    print(f"   Remaining non-R2 images: {remaining_broken}")

if __name__ == "__main__":
    main()
