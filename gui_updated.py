import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime
import csv
import os
import main_updated as main

root = tk.Tk()
root.title("AI Attendance System")
root.geometry("1000x650")

tk.Label(root, text="AI BASED ATTENDANCE SYSTEM",
         font=("Arial", 22, "bold")).pack(pady=10)

columns = ("Date", "Roll", "Name", "Time", "Period", "Type")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")
tree.pack(pady=10)

def load_today(role="STU"):
    tree.delete(*tree.get_children())
    today = datetime.now().strftime("%d-%m-%Y")
    
    if role=="STU":
        file = os.path.join(main.base_dir, f"Attendance_Student_{today}.csv")
    elif role=="TEA":
        file = os.path.join(main.base_dir, f"Attendance_Teacher_{today}.csv")
    else:
        file = os.path.join(main.base_dir, f"Attendance_Staff_{today}.csv")
        
    if not os.path.exists(file):
        return
    
    with open(file, "r") as f:
        r = csv.reader(f)
        header = next(r, None)
        for row in r:
            if role=="STU":
                tree.insert("", tk.END, values=row + [role])
            else:
                tree.insert("", tk.END, values=[row[0], "", row[1], row[2], row[3], role])

def start_cam():
    msg = main.start_attendance()
    if msg == "Camera Error":
        status_label.config(text="Camera Error")
    else:
        load_today()
        status_label.config(text="Attendance Done")

def print_any_date():
    d = simpledialog.askstring("Date", "Enter Date (DD-MM-YYYY)")
    if d is None: return
    role = simpledialog.askstring("Role", "Enter Role (STU/TEA/STF)")
    if role is None: return
    role = role.strip().upper()
    if role not in ("STU", "TEA", "STF"):
        status_label.config(text="Invalid Role!")
        return

    if role=="STU":
        file = os.path.join(main.base_dir, f"Attendance_Student_{d}.csv")
    elif role=="TEA":
        file = os.path.join(main.base_dir, f"Attendance_Teacher_{d}.csv")
    else:
        file = os.path.join(main.base_dir, f"Attendance_Staff_{d}.csv")

    if not os.path.exists(file):
        status_label.config(text="No record found!")
    else:
        os.startfile(file)

def admin_edit():
    # Admin password input
    pwd = simpledialog.askstring("Admin", "Enter Password", show="*")
    if pwd is None: return
    if pwd.strip().lower() != "admin123":
        status_label.config(text="Wrong Password")
        return

    # Ask for date
    d = simpledialog.askstring("Date", "Enter Date (DD-MM-YYYY)")
    if d is None: return

    # Open all three files if they exist
    files_opened = []
    file_paths = [
        os.path.join(main.base_dir, f"Attendance_Student_{d}.csv"),
        os.path.join(main.base_dir, f"Attendance_Teacher_{d}.csv"),
        os.path.join(main.base_dir, f"Attendance_Staff_{d}.csv")
    ]
    
    for file in file_paths:
        if os.path.exists(file):
            os.startfile(file)
            files_opened.append(os.path.basename(file))
    
    if files_opened:
        status_label.config(text=f"Opened: {', '.join(files_opened)}")
    else:
        status_label.config(text=f"No attendance files found for {d}!")

btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Start Attendance", command=start_cam).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Print Any Date", command=print_any_date).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="Admin Edit", command=admin_edit).grid(row=0, column=2, padx=10)
tk.Button(btn_frame, text="Exit", command=root.destroy).grid(row=0, column=3, padx=10)

status_label = tk.Label(root, text="", font=("Arial", 14))
status_label.pack(pady=10)

# Default load Student attendance
load_today(role="STU")
root.mainloop()
