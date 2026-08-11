import os
import shutil

source_dir = '/home/lukas/tmp/Photos-1-001/'
target_base = 'batch_incoming/'

files = sorted([f for f in os.listdir(source_dir) if f.endswith('.jpg') and ':Zone.Identifier' not in f])
folders = sorted([os.path.join(target_base, f) for f in os.listdir(target_base) if f.startswith('Mordor Ork_')])

# Extract number correctly
def get_num(folder_path):
    return int(os.path.basename(folder_path).split('_')[1])

target_folders = [f for f in folders if get_num(f) >= 15]

file_idx = 0
for folder in target_folders:
    for _ in range(3):
        if file_idx < len(files):
            src = os.path.join(source_dir, files[file_idx])
            dst = os.path.join(folder, files[file_idx])
            shutil.move(src, dst)
            file_idx += 1
