from scanner import scan_folder
from classifier import classify_file
from organizer import create_preview, organize_files, undo_organization
from duplicate_finder import find_duplicates
from statistics import get_statistics

folder = input("Enter the folder path to scan: ")

files = scan_folder(folder)

print("\n========== AI FILE BUTLER ==========\n")

print("Files found:", len(files))

for file in files:

    category = classify_file(file["extension"])
    file["category"] = category
    print("\nName:", file["name"])
    print("Extension:", file["extension"])
    print("Category:", category)
    print("Size:", file["size"], "bytes")
    print("Path:", file["path"])
    
preview = create_preview(files)
duplicates = find_duplicates(files)

print("\n========== DUPLICATE FILES ==========\n")

if duplicates:

    for item in duplicates:
        print("Original :", item["original"])
        print("Duplicate:", item["duplicate"])
        print()

else:
    print("No duplicate files found.")
print("\n========== ORGANIZATION PREVIEW ==========\n")

for item in preview:

    print(item["name"])
    print("   →", item["category"])
    print("   Destination:", item["destination"])
    print()
choice = input("Do you want to organize these files? (yes/no): ")

if choice.lower() == "yes":
    
    moved_files = organize_files(preview)

    print("\nFiles organized successfully!")

    undo = input("Do you want to undo this organization? (yes/no): ")

    if undo.lower() == "yes":
        undo_organization(moved_files)
        print("\nOrganization undone successfully!")

else:
    print("\nNo files were moved.")

duplicates = find_duplicates(files)

stats = get_statistics(files)

print("\n========== STORAGE STATISTICS ==========\n")

print("Total files:", stats["total_files"])
print("Total storage:", stats["total_size"], "bytes")

print("\nFiles by category:")

for category, count in stats["category_count"].items():
    print("   ", category, ":", count)

if stats["largest_file"]:
    print("\nLargest file:")
    print("   Name:", stats["largest_file"]["name"])
    print("   Size:", stats["largest_file"]["size"], "bytes")