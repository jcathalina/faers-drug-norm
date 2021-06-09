import os
import zipfile

from tqdm import tqdm


class FileManager:
    def __init__(self):
        pass

    @staticmethod
    def extract_faers(zip_dir: str):
        extract_path = os.path.join(zip_dir, "extracted")
        if not os.path.exists(extract_path):
            try:
                os.mkdir(extract_path)
            except PermissionError as e:
                print(f"Not enough permissions: {e}.")

        print("Extracting files...")
        for file in tqdm(os.listdir(zip_dir)):
            full_filename = os.path.join(zip_dir, file)
            if zipfile.is_zipfile(full_filename):
                with zipfile.ZipFile(full_filename) as zf:
                    zf.extractall(extract_path)

    @staticmethod
    def clean_up(extracted_dir: str):
        files_to_remove = []
        for f in os.listdir(extracted_dir):
            full_filename = os.path.join(extracted_dir, f)
            if os.path.isfile(full_filename) and full_filename.endswith((".pdf", ".PDF")):
                files_to_remove.append(full_filename)

        print(f"Removing {len(files_to_remove)} PDF files...")
        for file in tqdm(files_to_remove):
            try:
                os.remove(file)
            except FileNotFoundError as e:
                print(f"Not able to find {file}, error: {e}")
                continue





