#!/bin/bash
# Move and map data from /home/lukas/minis/processed to /home/lukas/minis/reviews
# Uses MAPPING.csv for path normalization.

SRC="/home/lukas/minis/processed"
DEST="/home/lukas/minis/reviews"
MAPPING="/home/lukas/minis/MAPPING.csv"

echo "Structuring reviews from $SRC to $DEST..."

# Load mapping
declare -A MAP
if [[ -f "$MAPPING" ]]; then
    while IFS=, read -r src_path dst_path; do
        if [[ "$src_path" != "Quelle_Pfad" ]]; then
            MAP["$src_path"]="$dst_path"
        fi
    done < "$MAPPING"
fi

# Find all files, process them
find "$SRC" -type f -name "*.md" | while read -r file; do
    rel_path="${file#$SRC/}"
    dir_part="$(dirname "$rel_path")"
    file_part="$(basename "$rel_path")"
    
    # Map directory if exists
    if [[ -n "${MAP[$dir_part]}" ]]; then
        new_dir="${MAP[$dir_part]}"
    else
        new_dir="$dir_part"
    fi
    
    # Destination
    dest_path="$DEST/$new_dir/$file_part"
    
    mkdir -p "$(dirname "$dest_path")"
    
    # Move
    mv "$file" "$dest_path"
    echo "Structured: $rel_path -> $new_dir/$file_part"
done

# Cleanup empty dirs
find "$SRC" -type d -empty -delete
echo "Structuring complete."
