import os
import re
import sys

# DEBUG: Print arguments
print(f"DEBUG: Arguments: {sys.argv}")

repo_url = "https://github.com/lkochniss/minis/blob/main/reviews"
base_dir = sys.argv[1]
print(f"DEBUG: Processing base_dir: {base_dir}")

def fix_file(file_path):
    print(f"DEBUG: Processing file: {file_path}")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Improved Pattern: ![alt](path) where path starts with ./ or just /
    # Matches: ![Alt Text](./path/to/img.jpg) or ![Alt Text](path/to/img.jpg)
    # Using '?' to make './' optional
    pattern = re.compile(r'!\[(.*?)\]\(\.?/?(.*?)\)')
    
    def replacement(match):
        alt = match.group(1)
        path = match.group(2)
        print(f"DEBUG: Found match: {match.group(0)}")
        
        # We need the directory path relative to base_dir
        directory = os.path.dirname(os.path.relpath(file_path, base_dir))
        # Handle the case where directory is '.'
        if directory == '.':
            new_url = f"{repo_url}/{path}"
        else:
            # Clean path from subdirectories if they are already in the file path
            new_url = f"{repo_url}/{directory}/{path}"
        print(f"DEBUG: Replacing with: ![{alt}]({new_url})")
        return f"![{alt}]({new_url})"
        
    new_content = pattern.sub(replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(new_content)

# Walk directory
for root, dirs, files in os.walk(base_dir):
    print(f"DEBUG: Walking: {root}")
    for file in files:
        if file.endswith('.md'):
            fix_file(os.path.join(root, file))
