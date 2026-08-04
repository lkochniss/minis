# ... später im Skript:
        # 3. Ziel-Struktur (Assets flach, Reviews strukturiert)
        norm_path = get_normalized_path(metadata.get('spielsystem', 'Sonstige'), metadata.get('fraktion', 'None'), metadata.get('einheit', base_name))
        target_dir_reviews = os.path.join(BASE_DIR, "reviews", norm_path)
        os.makedirs(target_dir_reviews, exist_ok=True)
        target_dir_assets = os.path.join(BASE_DIR, "assets")
        os.makedirs(target_dir_assets, exist_ok=True)
