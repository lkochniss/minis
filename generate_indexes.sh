#!/bin/bash
# Recursively generate index.md files for every directory in reviews/
# This makes navigation possible on GitHub Pages.

DEST="/home/lukas/minis/reviews"

# Find all directories under reviews/
find "$DEST" -type d | while read -r dir; do
    echo "Generating index for $dir..."
    
    # Define index file
    index_file="$dir/index.md"
    
    # Start fresh
    echo "# Index of $(basename "$dir")" > "$index_file"
    echo "" >> "$index_file"
    
    # 1. Add links to subdirectories (folders)
    echo "## Subfolders" >> "$index_file"
    find "$dir" -maxdepth 1 -mindepth 1 -type d | sort | while read -r subdir; do
        folder_name=$(basename "$subdir")
        echo "- [📁 $folder_name](./$folder_name/)" >> "$index_file"
    done
    echo "" >> "$index_file"

    # 2. Add links to files (md)
    echo "## Files" >> "$index_file"
    find "$dir" -maxdepth 1 -type f -not -name "index.md" -not -name ".*" | sort | while read -r file; do
        filename=$(basename "$file")
        echo "- [📄 $filename](./$filename)" >> "$index_file"
    done
done
echo "Recursive index generation complete."
