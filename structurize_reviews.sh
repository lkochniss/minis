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
    # rel_path ist jetzt direkt der Einheitenordner/Dateiname
    rel_path="${file#$SRC/}"
    unit_dir="$(dirname "$rel_path")"
    file_part="$(basename "$rel_path")"

    # Map directory (unit_dir) to destination path
    if [[ -n "${MAP[$unit_dir]}" ]]; then
        new_dir="${MAP[$unit_dir]}"
    else
        # Log and skip if not already logged
        if ! grep -qF "$unit_dir" "/home/lukas/minis/UNMAPPED.log" 2>/dev/null; then
             echo "$unit_dir" >> "/home/lukas/minis/UNMAPPED.log"
        fi
        echo "Skipping (unmapped): $unit_dir"
        continue
    fi

    # Destination
    # Remove hidden/control characters from path
    new_dir_cleaned=$(echo "$new_dir" | tr -d '[:cntrl:]')

    dest_path="$DEST/$new_dir_cleaned/$file_part"

    mkdir -p "$(dirname "$dest_path")"

    # Move
    mv "$file" "$dest_path"

    # Extract image filename from MD
    # Look for ![Miniatur](...) or ![...](...)
    # We need to get the filename.
    # Pattern: ![...](.../assets/filename.ext)
    
    # Get image path from MD
    image_rel_path=$(grep -oE "!\[Miniatur\]\([^)]*assets/([^)]+)\)" "$dest_path" | sed -E 's|!\[Miniatur\]\(([^)]*assets/([^)]+))\)|\2|')
    
    if [ -n "$image_rel_path" ]; then
        image_src_path="/home/lukas/minis/assets/$image_rel_path"
        if [ -f "$image_src_path" ]; then
            mv "$image_src_path" "$(dirname "$dest_path")/"
            # Update link in MD to local file
            sed -i -E "s|!\[Miniatur\]\([^)]*assets/([^)]+)\)|![Miniatur](./$(basename "$image_rel_path"))|g" "$dest_path"
        fi
    fi

    echo "Structured: $rel_path -> $new_dir_cleaned/$(basename "$dest_path")"
    done
# Cleanup empty dirs
find "$SRC" -type d -empty -delete
echo "Structuring complete."
