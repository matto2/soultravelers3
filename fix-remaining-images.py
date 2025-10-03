#!/usr/bin/env python3
"""
Fix remaining non-R2 image references
"""

import re
import glob

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_remaining_images(content):
    """Fix remaining broken image URLs"""
    changes = 0

    # Fix old Typepad URLs (these should have been caught earlier)
    old_typepad_count = len(re.findall(r'http://soultravelers3\.typepad\.com/\.a/[a-f0-9]+-[0-9]+wi', content))
    content = re.sub(
        r'http://soultravelers3\.typepad\.com/\.a/([a-f0-9]+)-[0-9]+wi',
        f'{R2_BASE}/\\1.jpg',
        content
    )
    changes += old_typepad_count

    # Remove wink emoji images (replace with actual emoji or just remove)
    wink_count = len(re.findall(r'!\[[^\]]*\]\(http://cdn\.theplanetd\.com/wp-includes/images/smilies/icon_wink\.gif\)', content))
    content = re.sub(
        r'!\[[^\]]*\]\(http://cdn\.theplanetd\.com/wp-includes/images/smilies/icon_wink\.gif\)',
        '😉',  # Replace with actual emoji
        content
    )
    changes += wink_count

    # Similar for digitalnomads.com wink
    wink2_count = len(re.findall(r'!\[[^\]]*\]\(http://www\.digitalnomads\.com/wp-includes/images/smilies/icon_wink\.gif\)', content))
    content = re.sub(
        r'!\[[^\]]*\]\(http://www\.digitalnomads\.com/wp-includes/images/smilies/icon_wink\.gif\)',
        '😉',
        content
    )
    changes += wink2_count

    # Remove Facebook external images (these are thumbnails that no longer work)
    fb_count = len(re.findall(r'!\[[^\]]*\]\(https://fbexternal[^)]+\)', content))
    content = re.sub(
        r'!\[[^\]]*\]\(https://fbexternal[^)]+\)',
        '',
        content
    )
    changes += fb_count

    # Fix old typepad stat tracking images (remove them)
    typepad_stat_count = len(re.findall(r'!\[[^\]]*\]\(http://www\.typepad\.com/t/stats[^)]+\)', content))
    content = re.sub(
        r'!\[[^\]]*\]\(http://www\.typepad\.com/t/stats[^)]+\)',
        '',
        content
    )
    changes += typepad_stat_count

    # Fix local image reference in about-us page
    local_count = len(re.findall(r'http://soultravelers3new\.local/typepad-images/', content))
    content = re.sub(
        r'http://soultravelers3new\.local/typepad-images/',
        f'{R2_BASE}/',
        content
    )
    changes += local_count

    return content, changes

def main():
    print("🔧 Fixing remaining non-R2 images...\n")

    files_modified = 0
    total_changes = 0

    for filepath in glob.glob('src/content/**/*.md', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()

            modified, changes = fix_remaining_images(original)

            if modified != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)
                files_modified += 1
                total_changes += changes
                print(f"✅ Fixed: {filepath} ({changes} changes)")

        except Exception as e:
            print(f"❌ Error: {filepath}: {e}")

    print(f"\n📊 SUMMARY:")
    print(f"   Files modified: {files_modified}")
    print(f"   Total changes: {total_changes}")

    # Count remaining non-R2 images
    remaining = 0
    files_with_remaining = []

    for filepath in glob.glob('src/content/**/*.md', recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content)
                for match in matches:
                    if not match.startswith('https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev'):
                        remaining += 1
                        if filepath not in files_with_remaining:
                            files_with_remaining.append((filepath, match))
        except:
            pass

    print(f"   Remaining non-R2 images: {remaining}")

    if files_with_remaining:
        print(f"\n🔍 Files with remaining non-R2 images:")
        for filepath, example in files_with_remaining[:10]:
            print(f"   {filepath}")
            print(f"      Example: {example}")

if __name__ == "__main__":
    main()
