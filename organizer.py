from pathlib import Path
from datetime import datetime


# =========================
# LOG MOVE OPERATION
# =========================

def log_operation(original, new):

    log_file = Path("logs") / "history.txt"

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        file.write(
            f"{time} | MOVED | "
            f"{original} -> {new}\n"
        )


# =========================
# LOG UNDO OPERATION
# =========================

def log_undo_operation(original, new):

    log_file = Path("logs") / "history.txt"

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        file.write(
            f"{time} | UNDONE | "
            f"{new} -> {original}\n"
        )


# =========================
# GET UNIQUE DESTINATION
# =========================

def get_unique_destination(destination):

    if not destination.exists():
        return destination

    counter = 1

    while True:

        new_name = (
            destination.stem
            + "_"
            + str(counter)
            + destination.suffix
        )

        new_destination = (
            destination.parent / new_name
        )

        if not new_destination.exists():
            return new_destination

        counter += 1


# =========================
# CREATE ORGANIZATION PREVIEW
# =========================

def create_preview(files):

    preview = []

    for file in files:

        source = Path(file["path"])
        category = file["category"]

        destination = (
            Path("organized")
            / category
            / file["name"]
        )

        preview.append({
            "name": file["name"],
            "source": source,
            "category": category,
            "destination": destination
        })

    return preview


# =========================
# ORGANIZE FILES
# =========================

def organize_files(preview):

    moved_files = []

    for item in preview:

        try:

            source = Path(
                item["source"]
            )

            if not source.exists():

                print(
                    "Source file not found:",
                    source
                )

                continue

            destination_folder = (
                item["destination"].parent
            )

            destination_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            safe_destination = (
                get_unique_destination(
                    item["destination"]
                )
            )

            safe_destination = (
                safe_destination.resolve()
            )

            source.rename(
                safe_destination
            )

            item["destination"] = (
                safe_destination
            )

            moved_files.append({
                "original": source,
                "new": safe_destination
            })

            log_operation(
                source,
                safe_destination
            )

            print(
                "Moved:",
                item["name"]
            )

        except (PermissionError, OSError) as error:

            print(
                "Could not move:",
                item["name"]
            )

            print(
                "Reason:",
                error
            )

            continue

    return moved_files


# =========================
# UNDO ORGANIZATION
# =========================

def undo_organization(moved_files):

    for item in reversed(moved_files):

        try:

            new_file = Path(
                item["new"]
            )

            original_file = Path(
                item["original"]
            )

            if not new_file.exists():

                print(
                    "File not found:",
                    new_file
                )

                continue

            if original_file.exists():

                print(
                    "Cannot restore:",
                    original_file,
                    "already exists."
                )

                continue

            new_file.rename(
                original_file
            )

            log_undo_operation(
                original_file,
                new_file
            )

            print(
                "Restored:",
                original_file
            )

        except (PermissionError, OSError) as error:

            print(
                "Could not restore:",
                item["original"]
            )

            print(
                "Reason:",
                error
            )

            continue