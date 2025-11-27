import os
import zipfile


def unzip(source: str, to_dir: str) -> bool:
    with zipfile.ZipFile(source, "r") as f:
        for file in f.namelist():
            if file.lower().endswith(".dcm"):
                f.extract(file, to_dir)


def zip_dir(dir_path: str, zip_path: str):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, start=dir_path)
                zf.write(abs_file, arcname=rel_path)
