import os
import uuid
import re
import shutil

# Verzeichnisse
ASSETS_DIR = "/home/lukas/minis/assets"
PROCESSED_DIR = "/home/lukas/minis/processed"
REVIEWS_DIR = "/home/lukas/minis/reviews"

# Mapping von altem Bildnamen zu neuem UUID-Bildnamen
image_mapping = {}

# 1. Migriere Assets
for filename in os.listdir(ASSETS_DIR):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        old_path = os.path.join(ASSETS_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()
        new_uuid = str(uuid.uuid4())
        new_filename = f"{new_uuid}{ext}"
        new_path = os.path.join(ASSETS_DIR, new_filename)
        
        shutil.move(old_path, new_path)
        image_mapping[filename] = new_filename
        print(f"Migrated asset: {filename} -> {new_filename}")

# 2. Funktion zum Update der MD-Dateien
def update_md_file(filepath, mapping):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pfad-Tiefe berechnen (relativ zu assets)
    depth = filepath.count('/') - 1
    rel_prefix = "../" * (depth)
    
    new_content = content
    # Ersetze alte Bildnamen durch neue UUID-Namen
    for old_name, new_name in mapping.items():
        # Suche nach dem alten Dateinamen im Pfad und ersetze ihn
        new_content = new_content.replace(old_name, new_name)
    
    # Pfade zu assets korrigieren (sicherstellen, dass sie auf den neuen Pfad zeigen)
    new_content = re.sub(r'!\[Miniatur\]\([^)]*assets/([^)]+)\)', 
                         rf'![Miniatur]({rel_prefix}assets/\1)', 
                         new_content)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
        
    # Markdown-Datei selbst umbenennen
    dir_path = os.path.dirname(filepath)
    new_md_name = f"{uuid.uuid4()}.md"
    os.rename(filepath, os.path.join(dir_path, new_md_name))
    print(f"Migrated MD: {filepath} -> {new_md_name}")

# 3. Durchlaufe processed und reviews
for directory in [PROCESSED_DIR, REVIEWS_DIR]:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                update_md_file(os.path.join(root, file), image_mapping)
EOF
