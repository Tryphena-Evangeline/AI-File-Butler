import hashlib


def get_file_hash(file_path):

    hash_object = hashlib.sha256()

    try:

        with open(file_path, "rb") as file:

            while chunk := file.read(4096):
                hash_object.update(chunk)

        return hash_object.hexdigest()

    except (PermissionError, OSError):

        print(
            "Could not read file:",
            file_path
        )

        return None


def find_duplicates(files):

    hashes = {}
    duplicates = []

    for file in files:

        file_hash = get_file_hash(
            file["path"]
        )

        if file_hash is None:
            continue

        if file_hash in hashes:

            duplicate_size = file["size"]

            duplicates.append({
                "original": hashes[file_hash],
                "duplicate": file["path"],
                "size": duplicate_size
            })

        else:

            hashes[file_hash] = file["path"]

    return duplicates