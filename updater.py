import os
import shutil
import tempfile
import subprocess
import sys
import requests
import zipfile
import psutil

REPO_ZIP_URL = "https://github.com/basu-10/termtools/archive/refs/heads/main.zip"
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def download_and_extract():
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "update.zip")

    with requests.get(REPO_ZIP_URL, stream=True) as r:
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    extracted_dir = next(os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)))
    return extracted_dir

def close_file_locks(filepath):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for item in proc.open_files():
                if filepath == item.path:
                    print(f"Closing process {proc.name()} (PID {proc.pid}) locking {filepath}")
                    proc.terminate()
                    proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def safe_remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except PermissionError:
        print(f"File locked: {path}")
        close_file_locks(path)
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        except Exception as e:
            print(f"Failed to remove {path}: {e}")

def replace_files(src_dir, dest_dir):
    for item in os.listdir(dest_dir):
        item_path = os.path.join(dest_dir, item)
        if item != os.path.basename(__file__):
            safe_remove(item_path)

    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    print("Updating...")
    extracted = download_and_extract()
    replace_files(extracted, APP_DIR)
    print("Update complete.")
    # subprocess.Popen([sys.executable, "main.py"])

