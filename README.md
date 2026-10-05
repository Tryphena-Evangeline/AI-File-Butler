# 🐻 AI File Butler

AI File Butler is a Python-based desktop application that helps users organize messy folders safely and efficiently.

It scans files, classifies them into categories, detects duplicate files, provides storage statistics, and organizes files with a preview and confirmation step. It also maintains operation history and supports undoing the latest organization operation.

---

## ✨ Features

- 📂 Folder scanning
- 🗂️ Automatic file classification
- 👀 Organization preview before changes
- 📁 Automatic folder organization
- 🔍 Duplicate file detection using SHA-256 hashing
- 📊 File and storage statistics
- ↩️ Undo the latest organization operation
- 📝 Operation history logging
- 🛡️ Filename collision protection
- 🐻 Cute and user-friendly Tkinter GUI

---

## 🛠️ Technologies Used

- **Python**
- **Tkinter** — Graphical User Interface
- **Pillow** — Bear Butler logo handling
- **hashlib** — SHA-256 duplicate detection
- **pathlib / os** — File and folder operations

---

## 📁 Project Structure

```text
AI-File-Butler/
│
├── data/
├── logs/
├── organized/
├── testfiles/
├── TestFolder/
│
├── config.py
├── main.py
├── scanner.py
├── classifier.py
├── organizer.py
├── duplicate_finder.py
├── statistics.py
├── gui.py
├── bear_butler_logo.png
└── README.md