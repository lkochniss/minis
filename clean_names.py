import os

def clean_names(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for name in dirnames + filenames:
            if '\r' in name:
                old_path = os.path.join(dirpath, name)
                new_name = name.replace('\r', '')
                new_path = os.path.join(dirpath, new_name)
                print(f"Renaming: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

if __name__ == "__main__":
    clean_names("/home/lukas/minis/reviews")
