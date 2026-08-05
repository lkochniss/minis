import os
import json
import hashlib
import shutil
import time
import argparse
from google import genai
from google.genai import types

# Konfiguration
INCOMING_DIR = "/home/lukas/minis/incoming"
BASE_DIR = "/home/lukas/minis"
PROCESSED_DIR = "/home/lukas/minis/processed"
STATE_FILE = "/home/lukas/minis/.migration_state.json"

# Argument Parser
parser = argparse.ArgumentParser(description="Miniatures Automatisierung")
parser.add_argument("--limit", type=int, default=None, help="Maximale Anzahl der zu verarbeitenden Bilder")
args = parser.parse_args()

client = genai.Client()

# --- FUNKTIONEN ---
def load_mapping(mapping_file):
    mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]: # Skip header
                if ',' in line:
                    src, dst = line.strip().split(',', 1)
                    mapping[src] = dst
    return mapping

def get_normalized_path(spielsystem, fraktion, einheit):
    raw_path = f"{spielsystem}/{fraktion}/{einheit.replace(' ', '-')}"
    mapping = load_mapping(os.path.join(BASE_DIR, "MAPPING.csv"))
    
    for src, dst in mapping.items():
        if raw_path.startswith(src):
            return raw_path.replace(src, dst)
    return raw_path

def get_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

# --- HAUPTPROGRAMM ---
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
else:
    state = {"processed_files": []}

processed_count = 0
for file in os.listdir(INCOMING_DIR):
    if args.limit and processed_count >= args.limit:
        break
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(INCOMING_DIR, file)

        if file_path in state["processed_files"]:
            continue

        base_name = os.path.splitext(file)[0].split('_')[0].replace("-", " ").title()
        print(f"Verarbeite: {file} (Erkannter Basis-Name: {base_name})")

        # 1. Bild mit KI analysieren
        time.sleep(60)
        try:
            file_ref = client.files.upload(file=file_path)
            prompt = f"""Analysiere das Bild der Miniatur mit dem Namen '{base_name}'.
            HINWEIS: Das Bild enthält mehrere zusammengesetzte Ansichten derselben Miniatur, um alle Details zu zeigen.
            Fülle das folgende Markdown-Template aus.
            WICHTIG: Verwende für die Einheit IMMER den SINGULAR.
            Antworte NUR mit einem JSON-Objekt, das diese Felder enthält:
            {{
              "spielsystem": "Name",
              "fraktion": "Name",
              "armee": "Name",
              "einheit": "Singular Name",
              "modelltyp": "Typ",
              "bewertung": "Zahl (float, z.B. 6,5)",
              "technik_ausfuehrung": "Bewertung [X]/10 und Analyse",
              "farbwahl_kontrast": "Bewertung [X]/10 und Analyse",
              "details_tiefe": "Bewertung [X]/10 und Analyse",
              "basierung": "Bewertung [X]/10 und Analyse",
              "gesamteindruck": "Bewertung [X]/10 und Analyse",
              "begruendung": "Begründung für die Bewertung"
            }}
            Wenn du etwas nicht sicher weißt, schreibe 'Unknown'."""

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[file_ref, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            metadata = json.loads(raw_text)
        except Exception as e:
            print(f"KI Analyse fehlgeschlagen für {file}, überspringe: {e}")
            continue 

        # 2. Hashing
        file_hash = get_hash(file_path)
        ext = os.path.splitext(file)[1].lower()
        new_filename = f"{base_name.replace(' ', '-').lower()}_{file_hash}{ext}"

        # 3. Ziel-Struktur (Assets flach, Reviews strukturiert)
        norm_path = get_normalized_path(metadata.get('spielsystem', 'Sonstige'), metadata.get('fraktion', 'None'), metadata.get('einheit', base_name))
        target_dir_processed = os.path.join(PROCESSED_DIR, norm_path)
        os.makedirs(target_dir_processed, exist_ok=True)
        target_dir_assets = os.path.join(BASE_DIR, "assets")
        os.makedirs(target_dir_assets, exist_ok=True)

        # 4. Bild verschieben
        target_image_path = os.path.join(target_dir_assets, new_filename)
        shutil.move(file_path, target_image_path)

        # 5. Markdown Review erstellen
        einheit_name = metadata.get('einheit', base_name)
        md_filename = f"{einheit_name.replace(' ', '-')}.md"
        md_path = os.path.join(target_dir_processed, md_filename)

        counter = 1
        while os.path.exists(md_path):
            md_filename = f"{einheit_name.replace(' ', '-')}_{counter}.md"
            md_path = os.path.join(target_dir_processed, md_filename)
            counter += 1

        rel_image_path = os.path.relpath(target_image_path, target_dir_processed)

        # Build Markdown content
        md_content = f"""---
kategorie: Miniatur
bewertung: {metadata.get('bewertung', '[Durchschnitt/10]')}
fertigstellung: ""
fraktion: {metadata.get('fraktion', 'None')}
armee: {metadata.get('armee', 'None')}
einheit: {einheit_name}
spielsystem: {metadata.get('spielsystem', 'Sonstige')}
modelltyp: {metadata.get('modelltyp', 'Unknown')}
hersteller: 
techniken: 
dauer: 
tags:
---

## Bilder
![Miniatur]({rel_image_path})

## Analyse

### 📊 Handwerkliche Bewertung (Objektiv)
- **1. Technik & Ausführung:** {metadata.get('technik_ausfuehrung', 'N/A')}
- **2. Farbwahl & Kontrast:** {metadata.get('farbwahl_kontrast', 'N/A')}
- **3. Details & Tiefe:** {metadata.get('details_tiefe', 'N/A')}
- **4. Basierung:** {metadata.get('basierung', 'N/A')}
- **5. Gesamteindruck:** {metadata.get('gesamteindruck', 'N/A')}

### 💡 Begründung der Bewertung
{metadata.get('begruendung', 'N/A')}
"""

        with open(md_path, 'w') as f:
            f.write(md_content)

        state["processed_files"].append(file_path)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

        print(f"Erfolgreich migriert: {einheit_name}")
        processed_count += 1

print("Automatisierung abgeschlossen.")
