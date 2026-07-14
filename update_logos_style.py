import os
import glob
import re

files = glob.glob('c:/Users/Lenovo/Documents/App_Innova/*.html')

# For index.html
try:
    with open('c:/Users/Lenovo/Documents/App_Innova/index.html', 'r', encoding='utf-8') as f:
        idx_content = f.read()
    
    idx_content = re.sub(
        r'<img src="assets/logo\.png" alt="Udec Parking Logo" style="height: 64px; object-fit: contain;">',
        '<img src="assets/logo.png" alt="Udec Parking Logo" style="height: 72px; object-fit: contain; mix-blend-mode: lighten; filter: drop-shadow(0 0 15px rgba(0, 168, 107, 0.4)); transform: scale(1.1); margin-left: -10px;">',
        idx_content
    )
    with open('c:/Users/Lenovo/Documents/App_Innova/index.html', 'w', encoding='utf-8') as f:
        f.write(idx_content)
except Exception as e:
    print(f"Error index: {e}")

# For sidebar files
pattern = r'<img src="assets/logo\.png" alt="Udec Parking Logo" style="height: 56px; object-fit: contain; margin-left: 8px;">'

replacement = '<img src="assets/logo.png" alt="Udec Parking Logo" style="height: 56px; width: 100%; object-fit: contain; mix-blend-mode: lighten; filter: drop-shadow(0 0 10px rgba(0, 168, 107, 0.3));">'

for f in files:
    if f.endswith('index.html'): continue
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        new_content = re.sub(pattern, replacement, content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
    except Exception as e:
        print(f"Error {f}: {e}")

print("Logos updated with blend modes")
