import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from scanner import scan_folder
from classifier import classify_file
from organizer import create_preview, organize_files, undo_organization
from duplicate_finder import find_duplicates
from statistics import get_statistics


# ============================================================
# COLORS
# ============================================================

BG = "#171A2B"
SIDEBAR = "#20213A"

CARD = "#292B43"
CARD_HOVER = "#333653"

TEXT = "#F7F4FA"
MUTED = "#B8B5C8"

PURPLE = "#C5A6E8"
PURPLE_DARK = "#51436B"

GREEN = "#A8DCCB"
GREEN_DARK = "#3C5952"

GOLD = "#E8C78F"
GOLD_DARK = "#5A4B3A"

RED = "#E99A9A"

BORDER = "#3A3C55"


# ============================================================
# WINDOW
# ============================================================

window = tk.Tk()

window.title("AI File Butler")
window.geometry("1100x650")
window.minsize(1000, 600)
window.configure(bg=BG)


# ============================================================
# VARIABLES
# ============================================================

selected_folder = None
scanned_files = []
current_preview = []
moved_files = []


# ============================================================
# PATHS
# ==============================       ==============================

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "bear_butler_logo.png"


# ============================================================
# LOGO
# ============================================================

logo_image = None

try:

    if LOGO_PATH.exists():

        logo_pil = Image.open(
            LOGO_PATH
        ).convert("RGBA")

        logo_pil.thumbnail(
            (75, 75),
            Image.Resampling.LANCZOS
        )

        logo_image = ImageTk.PhotoImage(
            logo_pil
        )

except Exception as error:

    print(
        "Could not load bear logo:",
        error
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_size(size):

    if size < 1024:

        return f"{size} B"

    elif size < 1024 * 1024:

        return f"{size / 1024:.1f} KB"

    elif size < 1024 * 1024 * 1024:

        return f"{size / (1024 * 1024):.1f} MB"

    else:

        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def update_status(message):

    status_label.config(
        text=message
    )


def add_activity(message):

    activity_text.config(
        state="normal"
    )

    activity_text.insert(
        "end",
        message + "\n\n"
    )

    activity_text.see(
        "end"
    )

    activity_text.config(
        state="disabled"
    )


def clear_results():

    activity_text.config(
        state="normal"
    )

    activity_text.delete(
        "1.0",
        "end"
    )

    activity_text.config(
        state="disabled"
    )

    add_activity(
        "Activity cleared."
    )

    update_status(
        "Ready"
    )


# ============================================================
# CHOOSE FOLDER
# ============================================================

def choose_folder():

    global selected_folder

    folder = filedialog.askdirectory(
        title="Choose a folder"
    )

    if not folder:

        return

    selected_folder = folder

    folder_label.config(
        text=folder
    )

    update_status(
        "Folder selected"
    )

    add_activity(
        f"Selected folder:\n{folder}"
    )


# ============================================================
# SCAN & ORGANIZE
# ============================================================

def scan_selected_folder():

    global scanned_files
    global current_preview
    global moved_files

    if not selected_folder:

        messagebox.showwarning(
            "No Folder Selected",
            "Please choose a folder first."
        )

        return

    try:

        # ----------------------------------------------------
        # SCAN
        # ----------------------------------------------------

        scanned_files = scan_folder(
            selected_folder
        )

        # ----------------------------------------------------
        # CLASSIFY
        # ----------------------------------------------------

        for file in scanned_files:

            file["category"] = classify_file(
                file["extension"]
            )

        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        total_size = sum(
            file["size"]
            for file in scanned_files
        )

        # ----------------------------------------------------
        # DUPLICATES
        # ----------------------------------------------------

        duplicates = find_duplicates(
            scanned_files
        )

        # ----------------------------------------------------
        # UPDATE DASHBOARD
        # ----------------------------------------------------

        files_value.config(
            text=str(
                len(scanned_files)
            )
        )

        duplicate_value.config(
            text=str(
                len(duplicates)
            )
        )

        storage_value.config(
            text=format_size(
                total_size
            )
        )

        update_status(
            f"Scanned {len(scanned_files)} files"
        )

        add_activity(
            f"✓ Scan completed\n"
            f"Files found: {len(scanned_files)}"
        )

        # ----------------------------------------------------
        # EMPTY FOLDER
        # ----------------------------------------------------

        if not scanned_files:

            add_activity(
                "The selected folder is empty."
            )

            messagebox.showinfo(
                "Empty Folder",
                "No files were found."
            )

            return

        # ----------------------------------------------------
        # CLASSIFICATION
        # ----------------------------------------------------

        add_activity(
            "──────── CLASSIFICATION ────────"
        )

        for file in scanned_files:

            add_activity(
                f"{file['name']}  →  "
                f"{file['category']}"
            )

        add_activity(
            "────────────────────────────────"
        )

        # ----------------------------------------------------
        # CREATE PREVIEW
        # ----------------------------------------------------

        current_preview = create_preview(
            scanned_files
        )

        add_activity(
            "──────── ORGANIZATION PREVIEW ────────"
        )

        for item in current_preview:

            if isinstance(item, dict):

                name = item.get(
                    "name",
                    Path(
                        item.get(
                            "source",
                            item.get(
                                "path",
                                ""
                            )
                        )
                    ).name
                )

                category = item.get(
                    "category",
                    "Other"
                )

                add_activity(
                    f"{name}  →  {category}"
                )

            else:

                add_activity(
                    str(item)
                )

        add_activity(
            "──────────────────────────────────────"
        )

        # ----------------------------------------------------
        # CONFIRMATION
        # ----------------------------------------------------

        confirm = messagebox.askyesno(
            "Confirm Organization",
            "The preview is ready.\n\n"
            "Do you want to organize these files?"
        )

        if not confirm:

            update_status(
                "Organization cancelled"
            )

            add_activity(
                "Organization cancelled by user."
            )

            return

        # ----------------------------------------------------
        # ORGANIZE
        #
        # IMPORTANT:
        # organize_files expects the preview.
        # Its returned value is saved as moved_files
        # so Undo can use it.
        # ----------------------------------------------------

        moved_files = organize_files(
            current_preview
        )

        # ----------------------------------------------------
        # ORGANIZATION COMPLETE
        # ----------------------------------------------------

        update_status(
            "Organization completed"
        )

        add_activity(
            "✓ Organization completed successfully."
        )

        if moved_files:

            for result in moved_files:

                add_activity(
                    str(result)
                )

        messagebox.showinfo(
            "Success",
            "Files have been organized successfully."
        )

    except Exception as error:

        update_status(
            "Operation failed"
        )

        messagebox.showerror(
            "Error",
            f"Something went wrong:\n\n{error}"
        )


# ============================================================
# FIND DUPLICATES
# ============================================================

def check_duplicates():

    if not selected_folder:

        messagebox.showwarning(
            "No Folder Selected",
            "Please choose a folder first."
        )

        return

    try:

        files = scan_folder(
            selected_folder
        )

        for file in files:

            file["category"] = classify_file(
                file["extension"]
            )

        duplicates = find_duplicates(
            files
        )

        duplicate_value.config(
            text=str(
                len(duplicates)
            )
        )

        add_activity(
            "──────── DUPLICATE CHECK ────────"
        )

        if not duplicates:

            add_activity(
                "✓ No duplicate files found."
            )

        else:

            add_activity(
                f"Found {len(duplicates)} "
                f"duplicate pair(s):"
            )

            for duplicate in duplicates:

                add_activity(
                    f"Original:\n"
                    f"{duplicate['original']}\n\n"
                    f"Duplicate:\n"
                    f"{duplicate['duplicate']}\n\n"
                    f"Size: "
                    f"{format_size(duplicate['size'])}"
                )

        add_activity(
            "────────────────────────────────"
        )

        update_status(
            f"{len(duplicates)} duplicate(s) found"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not check duplicates:\n\n{error}"
        )


# ============================================================
# STATISTICS
# ============================================================

def show_statistics():

    if not selected_folder:

        messagebox.showwarning(
            "No Folder Selected",
            "Please choose a folder first."
        )

        return

    try:

        files = scan_folder(
            selected_folder
        )

        for file in files:

            file["category"] = classify_file(
                file["extension"]
            )

        stats = get_statistics(
            files
        )

        files_value.config(
            text=str(
                stats["total_files"]
            )
        )

        storage_value.config(
            text=format_size(
                stats["total_size"]
            )
        )

        add_activity(
            "──────── FILE STATISTICS ────────"
        )

        add_activity(
            f"Total files: "
            f"{stats['total_files']}"
        )

        add_activity(
            f"Total storage: "
            f"{format_size(stats['total_size'])}"
        )

        add_activity(
            "Files by category:"
        )

        for category, count in stats[
            "category_count"
        ].items():

            add_activity(
                f"• {category}: {count}"
            )

        if stats["largest_file"]:

            largest = stats[
                "largest_file"
            ]

            add_activity(
                f"Largest file: "
                f"{largest['name']}"
            )

            add_activity(
                f"Size: "
                f"{format_size(largest['size'])}"
            )

        add_activity(
            "────────────────────────────────"
        )

        update_status(
            "Statistics generated"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not calculate statistics:\n\n{error}"
        )


# ============================================================
# UNDO
# ============================================================

def undo_last():

    global moved_files

    # --------------------------------------------------------
    # CHECK WHETHER THERE IS SOMETHING TO UNDO
    # --------------------------------------------------------

    if not moved_files:

        messagebox.showwarning(
            "Nothing to Undo",
            "There is no organization operation "
            "to undo in this session."
        )

        update_status(
            "Nothing to undo"
        )

        return

    try:

        # ----------------------------------------------------
        # UNDO
        # ----------------------------------------------------

        result = undo_organization(
            moved_files
        )

        add_activity(
            "✓ Last organization operation was undone."
        )

        if result:

            add_activity(
                str(result)
            )

        update_status(
            "Undo completed"
        )

        messagebox.showinfo(
            "Undo Complete",
            "Files have been restored."
        )

        # Clear stored operation after successful undo

        moved_files = []

    except Exception as error:

        update_status(
            "Undo failed"
        )

        messagebox.showerror(
            "Undo Error",
            f"Could not undo:\n\n{error}"
        )


# ============================================================
# SIDEBAR BUTTON
# ============================================================

def sidebar_button(
    parent,
    text,
    command,
    selected=False
):

    bg = (
        PURPLE_DARK
        if selected
        else SIDEBAR
    )

    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 9),
        bg=bg,
        fg=TEXT if selected else MUTED,
        activebackground=CARD_HOVER,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        anchor="w",
        padx=13,
        pady=9,
        cursor="hand2"
    )

    button.pack(
        fill="x",
        padx=10,
        pady=1
    )

    return button


# ============================================================
# ACTION CARD
# ============================================================

def create_action_card(
    parent,
    icon,
    title,
    description,
    button_text,
    command,
    accent
):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    # Accent line

    tk.Frame(
        card,
        bg=accent,
        height=4
    ).pack(
        fill="x"
    )

    inside = tk.Frame(
        card,
        bg=CARD
    )

    inside.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=13
    )

    tk.Label(
        inside,
        text=icon,
        font=("Segoe UI Symbol", 25),
        bg=CARD,
        fg=accent
    ).pack(
        anchor="w"
    )

    tk.Label(
        inside,
        text=title,
        font=("Segoe UI", 13, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        pady=(5, 4)
    )

    tk.Label(
        inside,
        text=description,
        font=("Segoe UI", 8),
        bg=CARD,
        fg=MUTED,
        justify="left",
        wraplength=210
    ).pack(
        anchor="w"
    )

    tk.Button(
        inside,
        text=button_text,
        command=command,
        font=("Segoe UI", 8, "bold"),
        bg=accent,
        fg=BG,
        activebackground=accent,
        activeforeground=BG,
        relief="flat",
        bd=0,
        padx=13,
        pady=7,
        cursor="hand2"
    ).pack(
        anchor="w",
        pady=(12, 0)
    )

    return card


# ============================================================
# SIDEBAR
# ============================================================

sidebar = tk.Frame(
    window,
    bg=SIDEBAR,
    width=180
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(
    False
)


# ============================================================
# BEAR LOGO
# ============================================================

logo_frame = tk.Frame(
    sidebar,
    bg=SIDEBAR
)

logo_frame.pack(
    pady=(25, 3)
)

if logo_image:

    logo_label = tk.Label(
        logo_frame,
        image=logo_image,
        bg=SIDEBAR,
        borderwidth=0
    )

    logo_label.pack()

else:

    tk.Label(
        logo_frame,
        text="🐻",
        font=("Segoe UI Emoji", 30),
        bg=SIDEBAR,
        fg=PURPLE
    ).pack()


# ============================================================
# BRANDING
# ============================================================

tk.Label(
    sidebar,
    text="AI FILE",
    font=("Segoe UI", 14, "bold"),
    bg=SIDEBAR,
    fg=TEXT
).pack(
    pady=(5, 0)
)

tk.Label(
    sidebar,
    text="BUTLER",
    font=("Segoe UI", 14, "bold"),
    bg=SIDEBAR,
    fg=PURPLE
).pack()

tk.Label(
    sidebar,
    text="your little file assistant",
    font=("Segoe UI", 7),
    bg=SIDEBAR,
    fg=MUTED
).pack(
    pady=(2, 20)
)


# ============================================================
# WORKSPACE
# ============================================================

tk.Label(
    sidebar,
    text="WORKSPACE",
    font=("Segoe UI", 7, "bold"),
    bg=SIDEBAR,
    fg=MUTED
).pack(
    anchor="w",
    padx=18,
    pady=(0, 5)
)


sidebar_button(
    sidebar,
    "⌂   Dashboard",
    lambda: update_status("Dashboard"),
    selected=True
)

sidebar_button(
    sidebar,
    "▣   Organize Files",
    scan_selected_folder
)

sidebar_button(
    sidebar,
    "○   Find Duplicates",
    check_duplicates
)

sidebar_button(
    sidebar,
    "▤   Statistics",
    show_statistics
)


# ============================================================
# SEPARATOR
# ============================================================

tk.Frame(
    sidebar,
    bg=BORDER,
    height=1
).pack(
    fill="x",
    padx=18,
    pady=18
)


# ============================================================
# TOOLS
# ============================================================

tk.Label(
    sidebar,
    text="TOOLS",
    font=("Segoe UI", 7, "bold"),
    bg=SIDEBAR,
    fg=MUTED
).pack(
    anchor="w",
    padx=18,
    pady=(0, 5)
)


sidebar_button(
    sidebar,
    "↶   Undo Last",
    undo_last
)

sidebar_button(
    sidebar,
    "×   Clear Activity",
    clear_results
)


# ============================================================
# SIDEBAR FOOTER
# ============================================================

footer = tk.Frame(
    sidebar,
    bg=SIDEBAR
)

footer.pack(
    side="bottom",
    pady=15
)

tk.Label(
    footer,
    text="✿",
    font=("Segoe UI Symbol", 18),
    bg=SIDEBAR,
    fg=GREEN
).pack()


# ============================================================
# MAIN AREA
# ============================================================

main_area = tk.Frame(
    window,
    bg=BG
)

main_area.pack(
    side="left",
    fill="both",
    expand=True
)


content = tk.Frame(
    main_area,
    bg=BG
)

content.pack(
    fill="both",
    expand=True,
    padx=28,
    pady=25
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    content,
    bg=BG
)

header.pack(
    fill="x"
)


tk.Label(
    header,
    text="Dashboard",
    font=("Segoe UI", 25, "bold"),
    bg=BG,
    fg=TEXT
).pack(
    side="left"
)


status_badge = tk.Frame(
    header,
    bg=CARD
)

status_badge.pack(
    side="right"
)


tk.Label(
    status_badge,
    text="●",
    font=("Segoe UI", 7),
    bg=CARD,
    fg=GREEN
).pack(
    side="left",
    padx=(10, 5),
    pady=10
)


status_label = tk.Label(
    status_badge,
    text="Ready",
    font=("Segoe UI", 8),
    bg=CARD,
    fg=MUTED
)

status_label.pack(
    side="left",
    padx=(0, 10),
    pady=10
)


tk.Label(
    content,
    text="Keep your files organized, safely and effortlessly.",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED
).pack(
    anchor="w",
    pady=(2, 17)
)


# ============================================================
# SELECTED FOLDER
# ============================================================

folder_card = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

folder_card.pack(
    fill="x",
    pady=(0, 13)
)


folder_info = tk.Frame(
    folder_card,
    bg=CARD
)

folder_info.pack(
    side="left",
    fill="both",
    expand=True,
    padx=20,
    pady=13
)


tk.Label(
    folder_info,
    text="SELECTED FOLDER",
    font=("Segoe UI", 7, "bold"),
    bg=CARD,
    fg=MUTED
).pack(
    anchor="w"
)


folder_label = tk.Label(
    folder_info,
    text="No folder selected",
    font=("Segoe UI", 9),
    bg=CARD,
    fg=TEXT,
    anchor="w"
)

folder_label.pack(
    anchor="w",
    pady=(4, 0)
)


tk.Button(
    folder_card,
    text="Choose Folder",
    command=choose_folder,
    font=("Segoe UI", 8, "bold"),
    bg=PURPLE,
    fg=BG,
    activebackground=PURPLE,
    activeforeground=BG,
    relief="flat",
    bd=0,
    padx=17,
    pady=9,
    cursor="hand2"
).pack(
    side="right",
    padx=15,
    pady=14
)


# ============================================================
# STATISTICS
# ============================================================

stats_frame = tk.Frame(
    content,
    bg=BG
)

stats_frame.pack(
    fill="x",
    pady=(0, 17)
)


def create_stat_card(
    parent,
    title,
    icon,
    value,
    accent
):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        side="left",
        fill="both",
        expand=True,
        padx=4
    )

    tk.Frame(
        card,
        bg=accent,
        height=3
    ).pack(
        fill="x"
    )

    inside = tk.Frame(
        card,
        bg=CARD
    )

    inside.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    top = tk.Frame(
        inside,
        bg=CARD
    )

    top.pack(
        fill="x"
    )

    tk.Label(
        top,
        text=title,
        font=("Segoe UI", 8),
        bg=CARD,
        fg=MUTED
    ).pack(
        side="left"
    )

    tk.Label(
        top,
        text=icon,
        font=("Segoe UI Symbol", 17),
        bg=CARD,
        fg=accent
    ).pack(
        side="right"
    )

    value_label = tk.Label(
        inside,
        text=value,
        font=("Segoe UI", 20, "bold"),
        bg=CARD,
        fg=TEXT
    )

    value_label.pack(
        anchor="w",
        pady=(5, 0)
    )

    return value_label


files_value = create_stat_card(
    stats_frame,
    "FILES SCANNED",
    "▤",
    "0",
    PURPLE
)


duplicate_value = create_stat_card(
    stats_frame,
    "DUPLICATES",
    "⌘",
    "0",
    GOLD
)


storage_value = create_stat_card(
    stats_frame,
    "STORAGE",
    "▣",
    "0 B",
    GREEN
)


# ============================================================
# ACTION TITLE
# ============================================================

tk.Label(
    content,
    text="What would you like to do?",
    font=("Segoe UI", 17, "bold"),
    bg=BG,
    fg=TEXT
).pack(
    anchor="w"
)


tk.Label(
    content,
    text="Choose an action below to get started.",
    font=("Segoe UI", 8),
    bg=BG,
    fg=MUTED
).pack(
    anchor="w",
    pady=(1, 10)
)


# ============================================================
# ACTION CARDS
# ============================================================

actions_frame = tk.Frame(
    content,
    bg=BG
)

actions_frame.pack(
    fill="x"
)


create_action_card(
    actions_frame,
    "□",
    "Scan & Organize",
    "Scan a folder, review the suggested categories, and safely organize your files.",
    "Start Scanning  →",
    scan_selected_folder,
    PURPLE
)


create_action_card(
    actions_frame,
    "⌕",
    "Find Duplicates",
    "Compare files using their content and identify duplicate copies.",
    "Check Duplicates  →",
    check_duplicates,
    GREEN
)


create_action_card(
    actions_frame,
    "▥",
    "View Statistics",
    "See file counts, storage usage, categories, and the largest file.",
    "View Statistics  →",
    show_statistics,
    GOLD
)


# ============================================================
# ACTIVITY
# ============================================================

activity_header = tk.Frame(
    content,
    bg=BG
)

activity_header.pack(
    fill="x",
    pady=(18, 5)
)


tk.Label(
    activity_header,
    text="Activity",
    font=("Segoe UI", 14, "bold"),
    bg=BG,
    fg=TEXT
).pack(
    side="left"
)


tk.Button(
    activity_header,
    text="Clear",
    command=clear_results,
    font=("Segoe UI", 7),
    bg=BG,
    fg=MUTED,
    activebackground=BG,
    activeforeground=TEXT,
    relief="flat",
    bd=0,
    cursor="hand2"
).pack(
    side="right"
)


activity_container = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

activity_container.pack(
    fill="both",
    expand=True
)


activity_text = tk.Text(
    activity_container,
    bg=CARD,
    fg=MUTED,
    insertbackground=TEXT,
    selectbackground=PURPLE_DARK,
    selectforeground=TEXT,
    font=("Consolas", 8),
    relief="flat",
    bd=0,
    wrap="word"
)

activity_text.pack(
    side="left",
    fill="both",
    expand=True,
    padx=12,
    pady=10
)

activity_text.config(
    state="disabled"
)


scrollbar = tk.Scrollbar(
    activity_container,
    command=activity_text.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)


activity_text.config(
    yscrollcommand=scrollbar.set
)


# ============================================================
# WELCOME
# ============================================================

add_activity(
    "Welcome to AI File Butler 🐻"
)

add_activity(
    "Choose a folder to begin organizing your files."
)


# ============================================================
# RUN
# ============================================================

window.mainloop()