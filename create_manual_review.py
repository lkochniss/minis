import os
import argparse
import hashlib
import shutil

BASE_DIR = "/home/lukas/minis"
REVIEWS_DIR = os.path.join(BASE_DIR, "reviews")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

parser = argparse.ArgumentParser(description="Manuelle Review Erstellung")
parser.add_argument("image", help="Pfad zum Bild")
parser.add_argument("name", help="Name der Einheit")
parser.add_argument("system", help="Spielsystem")
parser.add_argument("faction", help="Fraktion")
args = parser.parse_args()

def get_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

# 1. Hashing + Move
file_hash = get_hash(args.image)
ext = os.path.splitext(args.image)[1].lower()
new_filename = f"{file_hash}{ext}"
target_image_path = os.path.join(ASSETS_DIR, new_filename)
os.makedirs(ASSETS_DIR, exist_ok=True)
shutil.copy2(args.image, target_image_path)

# 2. Review erstellen
target_dir_reviews = os.path.join(REVIEWS_DIR, args.system, args.faction, args.name)
os.makedirs(target_dir_reviews, exist_ok=True)
md_path = os.path.join(target_dir_reviews, f"{args.name.replace(' ', '-')}.md")

rel_image_path = os.path.relpath(target_image_path, target_dir_reviews)

md_content = f"""---
kategorie: Miniatur
bewertung: [Durchschnitt/10]
fertigstellung: ""
fraktion: {args.faction}
armee: None
einheit: {args.name}
spielsystem: {args.system}
modelltyp: Unknown
hersteller: 
techniken: 
dauer: 
tags:
---

## Bilder
![Miniatur]({rel_image_path})

## Analyse

### 📊 Handwerkliche Bewertung (Objektiv)
- **1. Technik & Ausführung:** N/A
- **2. Farbwahl & Kontrast:** N/A
- **3. Details & Tiefe:** N/A
- **4. Basierung:** N/A
- **5. Gesamteindruck:** N/A

### 💡 Begründung der Bewertung
N/A
"""

with open(md_path, 'w') as f:
    f.write(md_content)

print(f"Review erstellt: {md_path}")
