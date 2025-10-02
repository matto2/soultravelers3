#!/usr/bin/env python3
"""
Fix linked images in blog posts.
Changes [![alt](thumb.jpg)](full.jpg) to ![alt](full.jpg)
"""

import re
import os
from pathlib import Path

R2_BASE = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_linked_images(content):
    """
    Replace [![alt](thumbnail)](full-image) with ![alt](full-image)
    """
    # Pattern: [![alt text](thumbnail-url)](full-url)
    pattern = r'\[!\[([^\]]*)\]\(' + re.escape(R2_BASE) + r'/[^\)]+\)\]\((' + re.escape(R2_BASE) + r'/[^\)]+)\)'

    def replacement(match):
        alt_text = match.group(1)
        full_url = match.group(2)
        return f'![{alt_text}]({full_url})'

    new_content = re.sub(pattern, replacement, content)

    return new_content

def main():
    blog_dir = Path("src/content/blog")

    modified_count = 0
    total_replacements = 0

    for index_file in blog_dir.glob("*/index.md"):
        content = index_file.read_text(encoding='utf-8')
        new_content = fix_linked_images(content)

        if new_content != content:
            # Count replacements
            replacements = len(re.findall(r'\[!\[([^\]]*)\]\(' + re.escape(R2_BASE), content))
            total_replacements += replacements

            index_file.write_text(new_content, encoding='utf-8')
            modified_count += 1
            print(f"Fixed {replacements} images in: {index_file.parent.name}")

    print(f"\n✓ Modified {modified_count} files")
    print(f"✓ Fixed {total_replacements} linked images")

if __name__ == "__main__":
    main()
