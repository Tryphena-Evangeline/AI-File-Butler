def get_statistics(files):
    
    total_files = len(files)

    total_size = 0

    category_count = {}

    category_size = {}

    largest_file = None

    for file in files:

        file_size = file["size"]

        total_size += file_size

        category = file["category"]

        # Count files by category
        if category not in category_count:
            category_count[category] = 0

        category_count[category] += 1

        # Calculate storage by category
        if category not in category_size:
            category_size[category] = 0

        category_size[category] += file_size

        # Find largest file
        if (
            largest_file is None
            or file_size > largest_file["size"]
        ):

            largest_file = file

    return {
        "total_files": total_files,
        "total_size": total_size,
        "category_count": category_count,
        "category_size": category_size,
        "largest_file": largest_file
    }