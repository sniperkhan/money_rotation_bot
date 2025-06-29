import os
import shutil
import time
from datetime import datetime, timedelta

FOLDER_PATH = "bots"  # Folder where all user bot folders are stored
EXPIRY_DAYS = 7

def delete_old_folders():
    if not os.path.exists(FOLDER_PATH):
        return

    for folder_name in os.listdir(FOLDER_PATH):
        folder_path = os.path.join(FOLDER_PATH, folder_name)
        if os.path.isdir(folder_path):
            creation_file = os.path.join(folder_path, "created.txt")

            if os.path.exists(creation_file):
                try:
                    with open(creation_file, "r") as f:
                        created_str = f.read().strip()

                    created_date = datetime.strptime(created_str, "%Y-%m-%d")
                    if datetime.now() - created_date > timedelta(days=EXPIRY_DAYS):
                        try:
                            shutil.rmtree(folder_path)
                            print(f"🗑 Deleted expired bot folder: {folder_name}")
                        except Exception as e:
                            print(f"❌ Could not delete folder {folder_name} | Reason: {e}")
                except Exception as e:
                    print(f"⚠ Error parsing created.txt for {folder_name}: {e}")
