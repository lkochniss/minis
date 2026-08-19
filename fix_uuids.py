import os
import re
from pathlib import Path

# Basis-Verzeichnis
ROOT_DIR = Path("reviews")

def fix_directory(directory):
    # Finde alle MD-Dateien
    md_files = list(directory.glob("*.md"))
    
    for md_file in md_files:
        if md_file.name == "index.md":
            continue
            
        # 1. Lese MD, um den Bild-Link zu finden
        with open(md_file, "r") as f:
            content = f.read()
            
        match = re.search(r'!\[Miniatur\]\(\./(.*\.jpg)\)', content)
        if not match:
            print(f"Kein Bildlink in {md_file.name} gefunden.")
            continue
            
        old_image_name = match.group(1)
        old_image_path = directory / old_image_name
        
        if not old_image_path.exists():
            print(f"Bild {old_image_name} aus {md_file.name} existiert nicht.")
            continue
            
        # 2. Neue UUID basierend auf der MD-Datei
        new_uuid = md_file.stem
        new_image_name = f"{new_uuid}.jpg"
        new_image_path = directory / new_image_name
        
        # 3. Bild umbenennen
        if old_image_name != new_image_name:
            print(f"Renaming {old_image_name} to {new_image_name}")
            os.rename(old_image_path, new_image_path)
            
            # 4. Link in MD anpassen
            new_content = content.replace(old_image_name, new_image_name)
            with open(md_file, "w") as f:
                f.write(new_content)
        else:
            print(f"Bild {new_image_name} ist bereits korrekt benannt.")

# Alle Unterordner in reviews durchsuchen
for subdir in ROOT_DIR.rglob("*"):
    if subdir.is_dir():
        fix_directory(subdir)
print("Fixing complete.")
