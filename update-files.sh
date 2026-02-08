#!/bin/bash

# Generate files.json with HTML files sorted by creation date (ascending)

# Get HTML files sorted by creation date, excluding index.html
files=$(stat -f "%B %N" *.html 2>/dev/null | grep -v "index.html" | sort -n | cut -d' ' -f2-)

# Start JSON array
echo "[" > files.json

# Add files to JSON
first=true
while IFS= read -r file; do
    if [ "$first" = true ]; then
        echo -n "  \"$file\"" >> files.json
        first=false
    else
        echo "," >> files.json
        echo -n "  \"$file\"" >> files.json
    fi
done <<< "$files"

# Close JSON array
echo "" >> files.json
echo "]" >> files.json

# Count files
count=$(echo "$files" | grep -c .)
echo "✓ files.json updated with $count HTML files"
