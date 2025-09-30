#!/usr/bin/env python3
"""
Fix image links so thumbnails link to full-size images.
Pattern: [![alt](thumb-150x150.jpg)](thumb-150x150.jpg)
Fix to: [![alt](thumb-150x150.jpg)](thumb.jpg)
"""

import re
import sys
from pathlib import Path

def fix_image_links(content):
    """Fix image links where both src and href point to thumbnails."""

    # Pattern to match: [![alt](URL/hash-SIZE.ext "title")](URL/hash-SIZE.ext)
    # We want to keep the size in the thumbnail but remove it from the link target

    # Match various size patterns: -150x150, -150x150-1, -500wi, -800wi, -pi, etc.
    pattern = r'(\[!\[[^\]]*\]\()(https://[^)]+?)(/6a00[a-f0-9]+)(-\d+x\d+(?:-\d+)?|-\d+wi|-pi)(\.[a-z]+)([^)]*\)\]\()(https://[^)]+?)\3\4\5(\))'

    def replacer(match):
        # Group 1: [![alt](
        # Group 2: Base URL
        # Group 3: Image hash
        # Group 4: Size suffix (to remove from href)
        # Group 5: Extension
        # Group 6: "title")](
        # Group 7: Link URL base
        # Group 8: )

        return f"{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}{match.group(5)}{match.group(6)}{match.group(7)}{match.group(3)}{match.group(5)}{match.group(8)}"

    return re.sub(pattern, replacer, content)

def main():
    blog_dir = Path("src/content/blog")

    if not blog_dir.exists():
        print("Error: src/content/blog directory not found")
        sys.exit(1)

    print("Fixing image links to point thumbnails to full-size images...")
    print("==============================================================")

    # Find all index.md files
    md_files = list(blog_dir.glob("*/index.md"))
    print(f"Total blog posts: {len(md_files)}")
    print()

    response = input("⚠️  Continue with fixing image links? (y/n) ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    print()
    print("Processing files...")

    modified_count = 0
    total_replacements = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            original = content

            # Fix the links
            content = fix_image_links(content)

            if content != original:
                md_file.write_text(content, encoding='utf-8')
                modified_count += 1

                # Count how many replacements were made
                replacements = len(re.findall(r'\]\([^)]*6a00[a-f0-9]+\.[a-z]+\)', content))
                total_replacements += replacements

        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    print()
    print("✅ Link fixing complete!")
    print()
    print(f"Files modified: {modified_count}")
    print(f"Total image links processed: {total_replacements}")
    print()

    # Check for remaining issues
    remaining = 0
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        # Look for patterns where both src and href still have size suffixes
        matches = re.findall(r'\]\([^)]*-150x150[^)]*\)\]\([^)]*-150x150[^)]*\)', content)
        remaining += len(matches)

    print(f"Remaining -150x150 thumbnail-to-thumbnail links: {remaining}")
    print()
    print("Next steps:")
    print("1. Review changes with: git diff src/content/blog | head -100")
    print("2. Test the site with: npm run dev")
    print("3. Commit changes if everything looks good")

if __name__ == "__main__":
    main()