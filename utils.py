import os
import glob

def delete_game_cache():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(script_dir, 'gamestate_cache')

    if not os.path.exists(cache_dir):
        print(f"No 'gamestate_cache' directory found at: {cache_dir}")
        return

    json_files = glob.glob(os.path.join(cache_dir, '**', '*.json'), recursive=True)

    if not json_files:
        print("No .json files found in 'gamestate_cache' or its subdirectories.")
        return
    
    deleted_file_count = 0

    for file_path in json_files:
        try:
            os.remove(file_path)
            deleted_file_count += 1
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    
    print("Successfully deleted {} gamestate files!".format(deleted_file_count))