import os
from pathlib import Path


def scan_folder(folder_path):

    files = []

    for root, directories, filenames in os.walk(folder_path):

        for filename in filenames:

            file_path = Path(root) / filename

            try:

                file_info = {
                    "name": filename,
                    "path": str(file_path),
                    "extension": file_path.suffix.lower(),
                    "size": file_path.stat().st_size
                }

                files.append(file_info)

            except (PermissionError, OSError):

                print(
                    "Could not access:",
                    file_path
                )

                continue

    return files