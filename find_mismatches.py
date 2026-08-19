import os
from pathlib import Path

def find_mismatches(base_dir):
    mismatches = []
    for root, dirs, files in os.walk(base_dir):
        md_files = {f: Path(root) / f for f in files if f.endswith('.md')}
        jpg_files = {f: Path(root) / f for f in files if f.endswith('.jpg')}
        
        md_uuids = {f.split('.')[0] for f in md_files.keys()}
        jpg_uuids = {f.split('.')[0] for f in jpg_files.keys()}
        
        # Files without a match
        for uuid in md_uuids - jpg_uuids:
            mismatches.append(f"MD file without JPG: {root}/{uuid}.md")
        for uuid in jpg_uuids - md_uuids:
            mismatches.append(f"JPG file without MD: {root}/{uuid}.jpg")
            
    return mismatches

mismatches = find_mismatches("reviews/Warhammer 40,000/Chaos/Death Guard")
for m in mismatches:
    print(m)
