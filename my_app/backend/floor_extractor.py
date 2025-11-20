import os
import json

def extract_floor_from_json(folder_path):
    """
    Search a folder recursively for JSON files and extract the "floor" node from each.

    Args:
    folder_path (str): The path to the folder to search for JSON files.

    Returns:
    dict: A dictionary where keys are file paths and values are the "floor" data or None if not found.
    """
    results = {}
    for root, dirs, files in os.walk(folder_path):

        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        floor = data.get('floor')
                        results[filepath] = floor
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {filepath}: {e}")
                    results[filepath] = None
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python floor_extractor.py <folder_path>")
        sys.exit(1)
    folder_path = sys.argv[1]
    floors = extract_floor_from_json(folder_path)
    print(len(floors.items()))
    for filepath, floor in floors.items():
        print(f"{filepath}: {floor}")
