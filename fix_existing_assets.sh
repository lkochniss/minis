#!/bin/bash
find /home/lukas/minis/reviews -type f -name "*.md" | while read -r md_file; do
    # Extract image filename from line matching ![Miniatur](.../assets/filename.ext)
    # Using perl or sed to handle regex properly.
    
    # Try to find the image filename in the MD file
    # Example line: ![Miniatur](../../../../../assets/1794e3c9-dd37-4587-a28f-9bdcb5a63b13.jpg)
    
    img_name=$(grep -oE "assets/[^)]+\.(jpg|jpeg|png)" "$md_file" | sed 's|assets/||')
    
    if [ -n "$img_name" ]; then
        src_path="/home/lukas/minis/assets/$img_name"
        dst_dir=$(dirname "$md_file")
        dst_path="$dst_dir/$img_name"

        if [ -f "$src_path" ]; then
            echo "Moving $img_name to $dst_dir"
            mv "$src_path" "$dst_path"
            # Update MD link to local file
            sed -i -E "s|!\[Miniatur\]\([^)]*assets/[^)]+\)|![Miniatur](./$img_name)|" "$md_file"
        fi
    fi
done
