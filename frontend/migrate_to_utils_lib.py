import os
import re

base_dir = r"d:\PROJECTS\Rectitude.AI new\frontend\src"
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(('.ts', '.tsx')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace @/lib/ with @/utils-lib/
            new_content = content.replace("@/lib/", "@/utils-lib/")
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {path}")
