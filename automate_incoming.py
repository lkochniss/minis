import os
import json
import hashlib
import shutil
import time
import argparse
import uuid
import re
import sys
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

def get_normalized_path(einheit):
    # Nur noch den Einheitsnamen verwenden
    return einheit.replace(' ', '-')

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

        # Vorab-Check: Ist es eine valide Bilddatei (kein LFS Pointer)?
        if os.path.getsize(file_path) < 1000:
            print(f"Datei {file} zu klein ({os.path.getsize(file_path)} bytes), überspringe.")
            continue

        # 1. Bild mit KI analysieren
        time.sleep(360)
        consecutive_errors = 0
        try:
            file_ref = client.files.upload(file=file_path)
            prompt = f"""Analysiere das Bild der Miniatur '{base_name}'.
            Antworte NUR mit einem JSON-Objekt.
            Felder: spielsystem, fraktion, armee, einheit (Singular), modelltyp, bewertung (Zahl), technik_ausfuehrung, farbwahl_kontrast, details_tiefe, basierung, gesamteindruck, begruendung.
            Bewertungs-Felder im Format "X/10 - kurze Analyse".
            Wenn unbekannt, schreibe 'Unknown'."""

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

            # Versuche, das JSON zu parsen; bei Fehler versuchen, mit einem Tipp auszugeben
            try:
                metadata = json.loads(raw_text)
                consecutive_errors = 0 # Erfolg: Zähler zurücksetzen
            except json.JSONDecodeError as e:
                print(f"JSON-Parsing fehlgeschlagen für {file}. Fehler: {e}")

                # Versuch 1: Reparatur von häufigen Fehlern
                repaired_text = re.sub(r'"\s*\n\s*"', '",\n"', raw_text)
                repaired_text = re.sub(r'(\d)\s*\n\s*"', r'\1,\n"', repaired_text)

                # Versuch 2: Versuch, das JSON zu vervollständigen
                if not repaired_text.strip().endswith('}'):
                    # Entferne eventuelle unvollständige Schlüssel/Werte am Ende
                    repaired_text = re.sub(r',\s*$', '', repaired_text.strip())
                    repaired_text += '}'

                try:
                    metadata = json.loads(repaired_text)
                    print("JSON erfolgreich repariert.")
                    consecutive_errors = 0 # Erfolg: Zähler zurücksetzen
                except json.JSONDecodeError:
                    print("JSON-Reparatur fehlgeschlagen. Versuche Extraktion per Regex.")
                    # Fallback: Extraktion per Regex
                    def extract_field(field, text):
                        match = re.search(fr'"{field}":\s*"(.*?)"', text, re.DOTALL)
                        if match:
                            return match.group(1)
                        # Suche nach Zahlenwerten ohne Anführungszeichen
                        match = re.search(fr'"{field}":\s*([^,}}]+)', text, re.DOTALL)
                        if match:
                            return match.group(1).strip().strip('"')
                        return 'Unknown'

                    fields = ['spielsystem', 'fraktion', 'armee', 'einheit', 'modelltyp', 'bewertung', 'technik_ausfuehrung', 'farbwahl_kontrast', 'details_tiefe', 'basierung', 'gesamteindruck', 'begruendung']
                    metadata = {field: extract_field(field, raw_text) for field in fields}

                    print("Extraktion per Regex abgeschlossen.")
                    consecutive_errors = 0 # Erfolg: Zähler zurücksetzen
        except Exception as e:
            if "INVALID_ARGUMENT" in str(e):
                print(f"Kritischer Fehler (INVALID_ARGUMENT) für {file}, beende Skript: {e}")
                sys.exit(1)
            
            # Fehler zählen, falls Server-Fehler (vereinfachte Prüfung)
            if any(code in str(e) for code in ["500", "502", "503", "504"]):
                consecutive_errors += 1
                print(f"KI Analyse fehlgeschlagen für {file} (Serverfehler {consecutive_errors}/3), überspringe: {e}")
                if consecutive_errors >= 3:
                    print("3 Serverfehler in Folge, breche ab.")
                    sys.exit(1)
            else:
                print(f"KI Analyse fehlgeschlagen für {file}, überspringe: {e}")
            continue

        # 2. Hashing
        file_hash = get_hash(file_path)
        ext = os.path.splitext(file)[1].lower()
        
        # UUID für eindeutige Zuweisung
        item_uuid = str(uuid.uuid4())
        new_filename = f"{item_uuid}{ext}"

        # 3. Ziel-Struktur (Assets flach, Reviews strukturiert)
        norm_path = get_normalized_path(base_name)
        target_dir_processed = os.path.join(PROCESSED_DIR, norm_path)
        os.makedirs(target_dir_processed, exist_ok=True)
        target_dir_assets = os.path.join(BASE_DIR, "assets")
        os.makedirs(target_dir_assets, exist_ok=True)

        # 4. Bild verschieben
        target_image_path = os.path.join(target_dir_assets, new_filename)
        shutil.move(file_path, target_image_path)

        # 5. Markdown Review erstellen
        einheit_name = metadata.get('einheit', base_name)
        md_filename = f"{item_uuid}.md"
        md_path = os.path.join(target_dir_processed, md_filename)

        rel_image_path = os.path.relpath(target_image_path, target_dir_processed)

        # Bewertung bereinigen (nur numerischen Wert extrahieren)
        raw_bewertung = str(metadata.get('bewertung', '0'))
        cleaned_bewertung = re.sub(r'(\d+(\.\d+)?)\s*/\s*10.*', r'\1', raw_bewertung)

        # Build Markdown content
        md_content = f"""---
        kategorie: Miniatur
        bewertung: {cleaned_bewertung}
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
