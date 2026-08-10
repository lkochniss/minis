#!/bin/bash
# Generate index.md files for each directory in reviews/
# This makes navigation possible on GitHub Pages.

DEST="/home/lukas/minis/reviews"

find "$DEST" -type d | while read -r dir; do
    echo "Generating index for $dir..."
    
    # Skip if root
    if [ "$dir" == "$DEST" ]; then
        continue
    fi
    
    # Create index.md
    index_file="$dir/index.md"
    echo "# Index of $(basename "$dir")" > "$index_file"
    echo "" >> "$index_file"
    
    # List files (excluding index.md)
    find "$dir" -maxdepth 1 -type f -not -name "index.md" -not -name ".*" | sort | while read -r file; do
        filename=$(basename "$file")
        echo "- [$filename](./$filename)" >> "$index_file"
    done
done
echo "Index generation complete."
