import os
import markdown
import re

def convert_md_to_html(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                html_path = os.path.join(root, file.replace('.md', '.html'))
                
                with open(md_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Convert links: [text](path/to/file.md) -> [text](path/to/file.html)
                # We need to be careful not to break external links
                text = re.sub(r'\]\((?!http)(.*?)\.md\)', r'](\1.html)', text)
                
                html = markdown.markdown(text, extensions=['extra', 'toc'])
                
                # Wrap in simple HTML structure
                full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 2rem; }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                # Optionally remove the original markdown file
                os.remove(md_path)

if __name__ == '__main__':
    convert_md_to_html('site')
