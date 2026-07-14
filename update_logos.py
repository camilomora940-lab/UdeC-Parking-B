import os
import glob
import re

files = glob.glob('c:/Users/Lenovo/Documents/App_Innova/*.html')

pattern = r'<div class="sidebar-logo">[\s\S]*?<div class="sidebar-logo-icon">🅿️</div>[\s\S]*?<div class="sidebar-logo-text">[\s\S]*?<div class="sidebar-logo-title">UdeC ParkApp</div>[\s\S]*?<div class="sidebar-logo-sub">Campus Concepción</div>[\s\S]*?</div>[\s\S]*?</div>'

replacement = '''<div class="sidebar-logo">
        <img src="assets/logo.png" alt="Udec Parking Logo" style="height: 56px; object-fit: contain; margin-left: 8px;">
      </div>'''

for f in files:
    if f.endswith('index.html'): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    new_content = re.sub(pattern, replacement, content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)
print("Updated logos")
