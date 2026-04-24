import os
import json

FOLDER = "obsidian/05_客戶"

def parse_md(file_path):
    data = {"name": os.path.basename(file_path).replace(".md", "")}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "::" in line:
                try:
                    k, v = line.split("::")
                    data[k.strip()] = v.strip()
                except:
                    pass
    return data


customers = []

for file in os.listdir(FOLDER):
    if file.endswith(".md"):
        customers.append(parse_md(os.path.join(FOLDER, file)))

os.makedirs("data", exist_ok=True)

with open("data/customers.json", "w", encoding="utf-8") as f:
    json.dump(customers, f, ensure_ascii=False, indent=2)

print("✅ updated")
