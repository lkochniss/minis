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
REVIEWS_DIR = "/home/lukas/minis/reviews"
STATE_FILE = "/home/lukas/minis/.migration_state.json"

# Argument Parser für Limit
parser = argparse.ArgumentParser(description="Miniatures Automatisierung")
parser.add_argument("--limit", type=int, default=None, help="Maximale Anzahl der zu verarbeitenden Bilder")
args = parser.parse_args()

client = genai.Client()

TEMPLATE_CONTENT = """---
kategorie: Miniatur
bewertung: [Durchschnitt/10]
fertigstellung: ""
fraktion: {fraktion}
armee: {armee}
einheit: {einheit}
spielsystem: {spielsystem}
modelltyp: {modelltyp}
hersteller: 
techniken: 
dauer: 
tags:
---

## Bilder
![Miniatur]({image_path})

## Analyse

### 📊 Handwerkliche Bewertung (Objektiv)
- **1. Technik & Ausführung:** [Analyse] ([X]/10)
- **2. Farbwahl & Kontrast:** [Analyse] ([X]/10)
- **3. Details & Tiefe:** [Analyse] ([X]/10)
- **4. Basierung:** [Analyse] ([X]/10)
- **5. Gesamteindruck:** [Analyse] ([X]/10)

*Durchschnitt:* [Durchschnittswert]

### 💡 Begründung der Bewertung
[Begründung: Warum X Punkte? Verweis auf Framework]
"""

# State Management
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
else:
    state = {"processed_files": []}

def get_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

# Process incoming
processed_count = 0
for file in os.listdir(INCOMING_DIR):
    if args.limit and processed_count >= args.limit:
        break
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(INCOMING_DIR, file)

        if file_path in state["processed_files"]:
            continue

        # Dateinamen-Extraktion (Name_Nummer -> Name)
        base_name = os.path.splitext(file)[0].split('_')[0].replace("-", " ").title()
        print(f"Verarbeite: {file} (Erkannter Basis-Name: {base_name})")

        # 1. Bild mit KI analysieren
        time.sleep(10) # Pause um Quota zu schonen
        try:
            file_ref = client.files.upload(file=file_path)
            prompt = f"""Analysiere das Bild der Miniatur mit dem Namen '{base_name}' und fülle das folgende Markdown-Template aus.
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
            metadata = json.loads(response.text)
        except Exception as e:
            print(f"KI Analyse fehlgeschlagen für {file}, überspringe: {e}")
            continue 

        # 2. Hashing (eindeutiger Dateiname für Assets)
        file_hash = get_hash(file_path)
        ext = os.path.splitext(file)[1].lower()
        new_filename = f"{base_name.replace(' ', '-').lower()}_{file_hash}{ext}"

        # 3. Ziel-Struktur (Assets flach, Reviews strukturiert)
        target_dir_reviews = os.path.join(BASE_DIR, "reviews", metadata.get('spielsystem', 'Sonstige'), metadata.get('fraktion', 'None'), metadata.get('einheit', base_name).replace(' ', '-'))
        os.makedirs(target_dir_reviews, exist_ok=True)
        target_dir_assets = os.path.join(BASE_DIR, "assets")
        os.makedirs(target_dir_assets, exist_ok=True)

        # 4. Bild verschieben
        target_image_path = os.path.join(target_dir_assets, new_filename)
        shutil.move(file_path, target_image_path)

        # 5. Markdown Review erstellen
        einheit_name = metadata.get('einheit', base_name)
        md_filename = f"{einheit_name.replace(' ', '-')}.md"
        md_path = os.path.join(target_dir_reviews, md_filename)

        counter = 1
        while os.path.exists(md_path):
            md_filename = f"{einheit_name.replace(' ', '-')}_{counter}.md"
            md_path = os.path.join(target_dir_reviews, md_filename)
            counter += 1

        rel_image_path = os.path.relpath(target_image_path, target_dir_reviews)

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

        # 6. State updaten
        state["processed_files"].append(file_path)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

        print(f"Erfolgreich migriert: {einheit_name}")
        processed_count += 1



print("Automatisierung abgeschlossen.")
