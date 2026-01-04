
import os
import yaml

TARGETS_DIR = "targets"

def extract_types():
    unique_types = set()
    
    for filename in os.listdir(TARGETS_DIR):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            path = os.path.join(TARGETS_DIR, filename)
            print(f"Scanning {filename}...")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    # Some files might be large, load safely
                    data = yaml.safe_load(f)
                    # Data structure commonly: list of dicts or dict of dicts
                    # Based on project usage, let's inspect structure
                    if isinstance(data, list):
                        for item in data:
                            if 'type' in item:
                                unique_types.add(item['type'])
                    elif isinstance(data, dict):
                         for key, item in data.items():
                            if isinstance(item, dict) and 'type' in item:
                                unique_types.add(item['type'])
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    print("\n--- Unique Types Found ---")
    for t in sorted(list(unique_types)):
        print(t)

if __name__ == "__main__":
    extract_types()
