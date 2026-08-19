import os
import re
from pathlib import Path

ROOT_DIR = Path("reviews")

def analyze_orphans(directory):
    md_files = list(directory.glob("*.md"))
    jpg_files = list(directory.glob("*.jpg"))
    
    referenced_images = set()
    broken_links = []
    
    # 1. Analysiere MDs auf Links
    for md_file in md_files:
        if md_file.name == "index.md":
            continue
            
        with open(md_file, "r") as f:
            content = f.read()
            
        matches = re.findall(r'!\[Miniatur\]\(\./(.*\.jpg)\)', content)
        for img_name in matches:
            img_path = directory / img_name
            if img_path.exists():
                referenced_images.add(img_name)
            else:
                broken_links.append((md_file, img_name))
                
    # 2. Finde JPEGs, die nicht referenziert sind
    orphaned_jpgs = [f for f in jpg_files if f.name not in referenced_images]
    
    return broken_links, orphaned_jpgs

all_broken_links = []
all_orphaned_jpgs = []

for subdir in ROOT_DIR.rglob("*"):
    if subdir.is_dir():
        broken, orphaned = analyze_orphans(subdir)
        all_broken_links.extend(broken)
        all_orphaned_jpgs.extend(orphaned)

print("--- Gebrochene Links (MD ohne existierendes Bild) ---")
for md, img in all_broken_links:
    print(f"MD: {md} | Link: {img}")

print("\n--- Verwaiste JPEGs (Nicht in MD referenziert) ---")
for jpg in all_orphaned_jpgs:
    print(f"JPG: {jpg}")
