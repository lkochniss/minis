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
    while IFS=$'\t' read -r src_path dst_path; do
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
        # Log and skip if not already logged
        if ! grep -qF "$dir_part" "/home/lukas/minis/UNMAPPED.log" 2>/dev/null; then
             echo "$dir_part" >> "/home/lukas/minis/UNMAPPED.log"
        fi
        echo "Skipping (unmapped): $rel_path"
        continue
    fi
    
    # Destination
    # Remove hidden/control characters from path
    new_dir_cleaned=$(echo "$new_dir" | tr -d '[:cntrl:]')
    dest_path="$DEST/$new_dir_cleaned/$file_part"
    
    mkdir -p "$(dirname "$dest_path")"
    
    # Move
    mv "$file" "$dest_path"

    # Update relative image paths
    depth=$(echo "$new_dir_cleaned" | tr -cd '/' | wc -c)
    rel_prefix=""
    for i in $(seq 1 $((depth + 2))); do rel_prefix="../$rel_prefix"; done
    sed -i "s|!\[Miniatur\](.*assets/|!\[Miniatur\]($rel_prefixassets/|g" "$dest_path"

    echo "Structured: $rel_path -> $new_dir_cleaned/$file_part"
    done

# Cleanup empty dirs
find "$SRC" -type d -empty -delete
echo "Structuring complete."
