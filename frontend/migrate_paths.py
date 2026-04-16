import os
import re

base_dir = r"d:\PROJECTS\Rectitude.AI new\frontend\src"
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match either double or single quotes and preserve them
            # Pattern: (quote char)(relative dots)(path)
            def replace_fn(match):
                quote = match.group(1)
                folder = match.group(2)
                return f"{quote}@/{folder}/"

            new_content = re.sub(r'([\'"])(?:\.\./)+(lib|components|hooks|api|types)/', replace_fn, content)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {path}")
