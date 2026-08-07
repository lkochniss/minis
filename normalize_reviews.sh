#!/bin/bash
# Normalize structure in /home/lukas/minis/reviews based on MAPPING.csv
# Mapps full paths relative to SRC

SRC="/home/lukas/minis/reviews"
MAPPING="/home/lukas/minis/MAPPING.csv"
UNMAPPED="/home/lukas/minis/UNMAPPED.log"

echo "Normalizing structure in $SRC..."
> "$UNMAPPED"

# Load mapping into associative array
declare -A MAP
while IFS=, read -r src_path dst_path; do
    if [[ "$src_path" != "Quelle_Pfad" ]]; then
        MAP["$src_path"]="$dst_path"
    fi
done < "$MAPPING"

# Traverse and move directories
# Find all directories under SRC
find "$SRC" -type d -depth | while read -r path; do
    [[ "$path" == "$SRC" ]] && continue
    
    # Get path relative to SRC
    rel_path="${path#$SRC/}"
    
    # Check if this rel_path is in MAP
    if [[ -n "${MAP[$rel_path]}" ]]; then
        target_path="$SRC/${MAP[$rel_path]}"
        
        if [[ "$path" != "$target_path" ]]; then
            mkdir -p "$(dirname "$target_path")"
            mv "$path" "$target_path"
            echo "Moved: $rel_path -> ${MAP[$rel_path]}"
            
            # Repariere Bildpfade in allen MDs im verschobenen Ordner
            find "$target_path" -name "*.md" | while read -r md_file; do
                depth=$(echo "$md_file" | tr -cd '/' | wc -c)
                rel_prefix=""
                for i in $(seq 1 $((depth))); do rel_prefix="../$rel_prefix"; done
                sed -i -E "s|!\[Miniatur\]\([^)]*assets/([^)]+)\)|![Miniatur](${rel_prefix}assets/\1)|g" "$md_file"
            done
        fi
    else
        echo "$rel_path" >> "$UNMAPPED"
    fi
done

echo "Normalization complete. Unmapped paths logged to $UNMAPPED."

echo "Cleaning up empty directories..."
find "$SRC" -type d -empty -delete
echo "Cleanup complete."
