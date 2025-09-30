#!/bin/bash

# Script to fix image links so thumbnails link to full-size images
# Pattern: [![alt](thumb-150x150.jpg)](thumb-150x150.jpg)
# Fix to: [![alt](thumb-150x150.jpg)](thumb.jpg)

set -e

echo "Fixing image links to point thumbnails to full-size images..."
echo "=============================================================="

# Count files before
TOTAL_FILES=$(find src/content/blog -name "index.md" | wc -l | tr -d ' ')
echo "Total blog posts: $TOTAL_FILES"
echo ""

echo "⚠️  IMPORTANT: Make sure you have a backup or can revert via git"
echo ""
read -p "Continue with fixing image links? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Processing files..."
echo ""

# Find all markdown files and fix the links
find src/content/blog -name "index.md" -type f | while read file; do
    # Use Perl for more powerful regex
    perl -i -pe '
        # Fix pattern: [![...](URL-SIZE.ext "...")](URL-SIZE.ext)
        # to: [![...](URL-SIZE.ext "...")](URL.ext)

        # Match markdown image links where both src and href have size suffix
        s{
            (                                    # Start capture group 1
                \[!\[                            # Opening [![
                [^\]]*                           # Alt text
                \]\(                             # Opening ](
                https://[^)]+?                   # URL start
            )                                    # End capture group 1
            (/6a00[a-f0-9]+)                     # Image hash (capture group 2)
            (-\d+x\d+(?:-\d+)?)                  # Size suffix like -150x150 or -150x150-1 (capture group 3)
            (\.[a-z]+)                           # Extension (capture group 4)
            (                                    # Start capture group 5
                [^)]*                            # Optional title
                \)\]                             # Closing )]
                \(                               # Opening ( for href
                https://[^)]+?                   # URL start for href
            )                                    # End capture group 5
            \2\3\4                               # Same hash + size + ext
            (\))                                 # Closing ) (capture group 6)
        }{$1$2$3$4$5$2$4$6}gx;                  # Replace: keep size in src, remove from href

        # Also handle -500wi, -800wi, -pi patterns
        s{
            (                                    # Start capture group 1
                \[!\[                            # Opening [![
                [^\]]*                           # Alt text
                \]\(                             # Opening ](
                https://[^)]+?                   # URL start
            )                                    # End capture group 1
            (/6a00[a-f0-9]+)                     # Image hash (capture group 2)
            (-(?:500wi|800wi|pi))                # Size suffix (capture group 3)
            (\.[a-z]+)                           # Extension (capture group 4)
            (                                    # Start capture group 5
                [^)]*                            # Optional title
                \)\]                             # Closing )]
                \(                               # Opening ( for href
                https://[^)]+?                   # URL start for href
            )                                    # End capture group 5
            \2\3\4                               # Same hash + size + ext
            (\))                                 # Closing ) (capture group 6)
        }{$1$2$3$4$5$2$4$6}gx;                  # Replace: keep size in src, remove from href
    ' "$file"
done

echo ""
echo "✅ Link fixing complete!"
echo ""

# Count patterns that might still need fixing
echo "Checking for remaining issues..."
REMAINING=$(grep -rE '\]\([^)]*-150x150[^)]*\)\]\([^)]*-150x150[^)]*\)' src/content/blog 2>/dev/null | wc -l | tr -d ' ')
echo "Remaining -150x150 thumbnail-to-thumbnail links: $REMAINING"

echo ""
echo "Next steps:"
echo "1. Review changes with: git diff src/content/blog | head -100"
echo "2. Test the site with: npm run dev"
echo "3. Commit changes if everything looks good"