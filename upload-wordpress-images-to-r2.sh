#!/bin/bash

# Upload WordPress images to R2 using Wrangler
# This script finds images from wordpress-images-for-r2.txt in the uploads folder
# and uploads them to R2 bucket using Cloudflare Wrangler

BUCKET_NAME="matts-media"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Wrangler is not installed. Install it with: npm install -g wrangler"
    exit 1
fi

# Read the wordpress images list
if [ ! -f "wordpress-images-for-r2.txt" ]; then
    echo "wordpress-images-for-r2.txt not found!"
    exit 1
fi

# Counter for progress
total=$(grep -v '^#' wordpress-images-for-r2.txt | grep -v '^$' | wc -l | tr -d ' ')
count=0
uploaded=0
skipped=0
missing=0

echo "Total images to process: $total"
echo "Searching in uploads folder..."
echo ""

# Process each image
while IFS= read -r filename; do
    # Skip comments and empty lines
    [[ "$filename" =~ ^#.*$ ]] && continue
    [[ -z "$filename" ]] && continue

    count=$((count + 1))

    # Find the file in uploads folder (it could be in any year subfolder)
    found_file=$(find uploads -type f -name "$filename" | head -1)

    if [ -z "$found_file" ]; then
        echo "[$count/$total] MISSING: $filename"
        missing=$((missing + 1))
    else
        # Upload to R2 using Wrangler
        echo "[$count/$total] Uploading: $filename"
        wrangler r2 object put "$BUCKET_NAME/$filename" --file="$found_file" 2>&1

        if [ $? -eq 0 ]; then
            uploaded=$((uploaded + 1))
        else
            skipped=$((skipped + 1))
        fi
    fi
done < <(grep -v '^#' wordpress-images-for-r2.txt | grep -v '^$')

echo ""
echo "===== Upload Summary ====="
echo "Total processed: $count"
echo "Successfully uploaded: $uploaded"
echo "Skipped/failed: $skipped"
echo "Missing files: $missing"
