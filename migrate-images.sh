#!/bin/bash

# Script to replace TypePad image URLs with Cloudflare R2 URLs
# This will replace all occurrences in markdown files

set -e

R2_BASE_URL="https://pub-ac94b3f306b24c0dba4238943c97f2e1.r2.dev"

echo "Starting image URL migration from TypePad to Cloudflare R2..."
echo "================================================"

# Count files before
TOTAL_FILES=$(find src/content/blog -name "index.md" | wc -l | tr -d ' ')
echo "Total blog posts: $TOTAL_FILES"

AFFECTED_FILES=$(grep -rl "soultravelers3\.typepad\.com" src/content/blog 2>/dev/null | wc -l | tr -d ' ')
echo "Files with TypePad URLs: $AFFECTED_FILES"
echo ""

# Backup reminder
echo "⚠️  IMPORTANT: Make sure you have a backup or can revert via git"
echo ""
read -p "Continue with replacement? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Processing files..."

# Replace all TypePad URL variations
# Pattern 1: https://soultravelers3.typepad.com/...
find src/content/blog -name "index.md" -type f -exec sed -i '' \
    's|https://soultravelers3\.typepad\.com/|'"$R2_BASE_URL"'/|g' {} +

# Pattern 2: http://soultravelers3.typepad.com/...
find src/content/blog -name "index.md" -type f -exec sed -i '' \
    's|http://soultravelers3\.typepad\.com/|'"$R2_BASE_URL"'/|g' {} +

echo ""
echo "✅ Replacement complete!"
echo ""

# Count remaining TypePad URLs
REMAINING=$(grep -r "soultravelers3\.typepad\.com" src/content/blog 2>/dev/null | wc -l | tr -d ' ')
echo "Remaining TypePad URLs: $REMAINING"

if [ "$REMAINING" -eq 0 ]; then
    echo "🎉 All TypePad URLs have been replaced!"
else
    echo "⚠️  Some TypePad URLs may remain. Check manually."
fi

echo ""
echo "Next steps:"
echo "1. Review changes with: git diff"
echo "2. Test the site with: npm run dev"
echo "3. Commit changes if everything looks good"