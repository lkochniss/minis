#!/bin/bash
# Normalize structure in /home/lukas/minis/reviews based on MAPPING.csv

SRC="/home/lukas/minis/reviews"
MAPPING="/home/lukas/minis/MAPPING.csv"

echo "Normalizing structure in $SRC..."

# Load mapping
declare -A MAP
while IFS=, read -r src_part dst_part; do
    if [[ "$src_part" != "Quelle" ]]; then
        MAP["$src_part"]="$dst_part"
    fi
done < "$MAPPING"

# Traverse and rename
# Use find to get deepest items first to avoid parent rename issues
UNMAPPED="/home/lukas/minis/UNMAPPED.log"
> "$UNMAPPED"

find "$SRC" -depth | while read -r path; do
    # Skip base
    [[ "$path" == "$SRC" ]] && continue
    
    # Get base name
    base=$(basename "$path")
    
    # Map if exists
    if [[ -n "${MAP[$base]}" ]]; then
        new_base="${MAP[$base]}"
        # If mapping contains /, handle directory creation
        if [[ "$new_base" == *"/"* ]]; then
            new_dir="$(dirname "$path")/$new_base"
            mkdir -p "$(dirname "$new_dir")"
            mv "$path" "$new_dir"
            echo "Renamed/Moved: $path -> $new_dir"
        else
            new_path="$(dirname "$path")/$new_base"
            mv "$path" "$new_path"
            echo "Renamed: $path -> $new_path"
        fi
    else
        # Log unmapped
        echo "$path" >> "$UNMAPPED"
    fi
done

echo "Normalization complete. Unmapped items logged to $UNMAPPED."

echo "Cleaning up empty directories..."
find "$SRC" -type d -empty -delete
echo "Cleanup complete."
