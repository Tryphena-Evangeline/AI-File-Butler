from config import FILE_CATEGORIES


def classify_file(extension):

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:
            return category

    return "Other"