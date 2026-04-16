import os
import re

base_dir = r"d:\PROJECTS\Rectitude.AI new\frontend\src"
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix mismatched quotes from previous run
            # Pattern: "(@/path)'
            new_content = re.sub(r'"(@/(?:lib|components|hooks|api|types)/[^"\']+)\'', r"'\1'", content)
            # Pattern: '(@/path)"
            new_content = re.sub(r"'(@/(?:lib|components|hooks|api|types)/[^'\"]+)\"", r'"\1"', new_content)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed quotes in: {path}")
