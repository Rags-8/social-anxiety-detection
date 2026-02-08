
# Script to cleanly resolve merge conflicts by favoring HEAD (Local) content
import os

file_path = "streamlit_app.py"
if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
conflict_count = 0

for line in lines:
    if "<<<<<<< HEAD" in line:
        print(f"Found HEAD marker at line {len(new_lines)+1}")
        conflict_count += 1
        continue  # Keep HEAD content, just remove marker
    
    if "=======" in line:
        print(f"Found DIVIDER marker. Skipping remote content...")
        skip = True
        continue
    
    if ">>>>>>>" in line:
        print(f"Found END marker. Stopping skip.")
        skip = False
        continue
        
    if not skip:
        new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Resolved {conflict_count} conflict blocks. Saved to {file_path}.")
