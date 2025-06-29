import os
import datetime
import shutil

def delete_old_folders():
    base_dir = os.getcwd()
    created_file = os.path.join(base_dir, "created.txt")

    if os.path.exists(created_file):
        with open(created_file, "r") as f:
            created_str = f.read().strip()

        try:
            created_date = datetime.datetime.fromisoformat(created_str)
            now = datetime.datetime.now()
            days_passed = (now - created_date).days

            if days_passed > 7:
                print("🗑 Bot expired. More than 7 days old. Deleting...")
                os.chdir("..")  # Go back one level from current bot folder
                shutil.rmtree(base_dir)
            else:
                print(f"✅ Bot is still active. Days passed: {days_passed}")
        except Exception as e:
            print(f"⚠ Error checking expiry: {e}")
    else:
        print("⚠ created.txt not found.")
