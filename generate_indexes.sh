#!/bin/bash
# Recursively generate index.md files for every directory in reviews/
# Lists only subfolders and .md files (excluding index.md).

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
    # Exclude hidden folders like .git if any exist, just in case
    find "$dir" -maxdepth 1 -mindepth 1 -type d -not -name ".*" | sort | while read -r subdir; do
        folder_name=$(basename "$subdir")
        echo "- [📁 $folder_name](./$folder_name/)" >> "$index_file"
    done
    echo "" >> "$index_file"

    # 2. Add links to files (only .md files)
    echo "## Files" >> "$index_file"
    find "$dir" -maxdepth 1 -type f -name "*.md" -not -name "index.md" | sort | while read -r file; do
        filename=$(basename "$file")
        echo "- [📄 $filename](./$filename)" >> "$index_file"
    done
done
echo "Clean index generation complete."
