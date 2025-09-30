#!/usr/bin/env python3
"""
Fix WordPress local dev URLs to point to R2 storage.
Pattern: http://soultravelers3new.local/wp-content/uploads/2025/09/6a00...jpg
Fix to: https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev/6a00...jpg
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

R2_BASE_URL = "https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

def fix_wordpress_urls(content):
    """Fix WordPress local dev URLs to point to R2."""

    # Pattern: http://soultravelers3new.local/wp-content/uploads/YYYY/MM/filename
    # Extract just the filename and map to R2
    pattern = r'https?://soultravelers3new\.local/wp-content/uploads/\d{4}/\d{2}/([^"\s)]+)'

    def replacer(match):
        filename = match.group(1)
        return f"{R2_BASE_URL}/{filename}"

    return re.sub(pattern, replacer, content)

def extract_wordpress_images(content):
    """Extract all WordPress image filenames from content."""
    pattern = r'https?://soultravelers3new\.local/wp-content/uploads/\d{4}/\d{2}/([^"\s)]+)'
    matches = re.findall(pattern, content)
    return [m for m in matches]

def main():
    blog_dir = Path("src/content/blog")

    if not blog_dir.exists():
        print("Error: src/content/blog directory not found")
        sys.exit(1)

    print("Fixing WordPress local dev URLs to point to R2...")
    print("===================================================")

    # Find all index.md files
    md_files = list(blog_dir.glob("*/index.md"))
    print(f"Total blog posts: {len(md_files)}")
    print()

    # First pass: collect all WordPress images
    print("Scanning for WordPress media URLs...")
    all_wp_images = set()
    files_with_wp_urls = []

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            wp_images = extract_wordpress_images(content)
            if wp_images:
                all_wp_images.update(wp_images)
                files_with_wp_urls.append(md_file)
        except Exception as e:
            print(f"Error scanning {md_file}: {e}")

    print(f"Found {len(all_wp_images)} unique WordPress images")
    print(f"Found in {len(files_with_wp_urls)} blog posts")
    print()

    response = input("⚠️  Continue with replacing WordPress URLs? (y/n) ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    print()
    print("Processing files...")

    modified_count = 0
    total_replacements = 0

    for md_file in files_with_wp_urls:
        try:
            content = md_file.read_text(encoding='utf-8')
            original = content

            # Count replacements before
            before_count = len(re.findall(r'soultravelers3new\.local/wp-content/uploads', content))

            # Fix the URLs
            content = fix_wordpress_urls(content)

            # Count replacements after
            after_count = len(re.findall(r'soultravelers3new\.local/wp-content/uploads', content))
            replacements_made = before_count - after_count

            if content != original:
                md_file.write_text(content, encoding='utf-8')
                modified_count += 1
                total_replacements += replacements_made

        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    print()
    print("✅ WordPress URL replacement complete!")
    print()
    print(f"Files modified: {modified_count}")
    print(f"Total URLs replaced: {total_replacements}")
    print()

    # Check for remaining WordPress URLs
    remaining_count = 0
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        remaining_count += len(re.findall(r'soultravelers3new\.local/wp-content/uploads', content))

    print(f"Remaining WordPress URLs: {remaining_count}")

    if remaining_count > 0:
        print()
        print("⚠️  Some WordPress URLs remain (likely non-media URLs)")

    print()
    print("Creating list of images that should be in R2...")

    # Save the list of images for verification
    output_file = Path("wordpress-images-for-r2.txt")
    with output_file.open('w') as f:
        f.write("# WordPress images that should be available in R2\n")
        f.write(f"# Total: {len(all_wp_images)} unique images\n")
        f.write("# Format: filename (as found in markdown)\n\n")
        for img in sorted(all_wp_images):
            f.write(f"{img}\n")

    print(f"✅ Saved image list to: {output_file}")
    print()
    print("Next steps:")
    print("1. Review the image list in wordpress-images-for-r2.txt")
    print("2. Verify these images exist in your R2 bucket")
    print("3. Test the site with: npm run dev")
    print("4. Check for broken images")
    print("5. Upload any missing images to R2")
    print("6. Commit changes if everything looks good")

if __name__ == "__main__":
    main()