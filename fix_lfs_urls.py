import os
import re
import sys

repo_url = "https://github.com/lkochniss/minis/blob/main/reviews"
base_dir = sys.argv[1]

def fix_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find ![alt](path) where path starts with ./
    pattern = re.compile(r'!\[(.*?)\]\(\./(.*?)\)')
    
    def replacement(match):
        alt = match.group(1)
        path = match.group(2)
        # We need the directory path relative to base_dir
        directory = os.path.dirname(os.path.relpath(file_path, base_dir))
        # Handle the case where directory is '.'
        if directory == '.':
            new_url = f"{repo_url}/{path}"
        else:
            new_url = f"{repo_url}/{directory}/{path}"
        return f"![{alt}]({new_url})"
        
    new_content = pattern.sub(replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(new_content)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md'):
            fix_file(os.path.join(root, file))
