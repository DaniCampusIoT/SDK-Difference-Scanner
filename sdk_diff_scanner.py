import os
import json
import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from difflib import unified_diff
import csv
from html import escape
import tkinter as tk
from tkinter import scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD

# Configuration file name
CONFIG_FILE = "config.json"
# Keywords to highlight in HTML diff output
KEYWORDS = ['Init', 'Connect', 'ReadData', 'WriteLog', 'Config', 'Error']

# Supported file extensions and their labels for selection
EXTENSION_OPTIONS = [
    ('.c', 'C source'),
    ('.h', 'C header'),
    ('.cpp', 'C++ source'),
    ('.hpp', 'C++ header'),
    ('.cc', 'Alt C++ src'),
    ('.hh', 'Alt C++ hdr'),
    ('.py', 'Python'),
    ('.java', 'Java'),
    ('.js', 'JavaScript'),
    ('.ts', 'TypeScript'),
    ('.go', 'Go'),
    ('.rb', 'Ruby'),
    ('.sh', 'Shell'),
    ('.bat', 'Batch'),
    ('.pl', 'Perl'),
    ('.php', 'PHP'),
    ('.cs', 'C#'),
    ('.swift', 'Swift'),
    ('.kt', 'Kotlin'),
    ('.cfg', 'Config'),
    ('.conf', 'Config'),
    ('.ini', 'Config'),
    ('.json', 'JSON'),
    ('.yaml', 'YAML'),
    ('.yml', 'YAML'),
    ('.xml', 'XML'),
    ('.xsd', 'XML'),
    ('.xslt', 'XML'),
    ('.txt', 'Text'),
    ('.md', 'Markdown'),
    ('.rst', 'reST'),
    ('.log', 'Log'),
    ('.gdb', 'GDB script'),
    ('.map', 'Map'),
    ('.make', 'Make'),
    ('Makefile', 'Makefile'),
    ('.gradle', 'Gradle'),
    ('.cmake', 'CMake'),
    ('.mk', 'Make'),
    ('.dockerfile', 'Dockerfile'),
    ('Dockerfile', 'Dockerfile'),
    ('.props', 'Props'),
    ('.settings', 'Settings'),
    ('.gitignore', 'Gitignore'),
    ('.editorconfig', 'Editorconfig')
]
# Dictionary to hold extension selection variables
ext_vars = {}

def get_selected_extensions():
    """Return tuple of selected file extensions."""
    return tuple(ext for ext, var in ext_vars.items() if var.get())

# Globals for storing diff results and file status
diffs_by_file = {}
file_status_dict = {}

def save_config(old_sdk_path, new_sdk_path, output_dir):
    """Save SDK paths and output directory to config file."""
    config = {
        "old_sdk_path": old_sdk_path,
        "new_sdk_path": new_sdk_path,
        "output_dir": output_dir,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    """Load SDK paths and output directory from config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            print("Loaded config:", data)
            return data
    return {}

def compare_sdk_directories_gui(old_sdk_path, new_sdk_path, output_dir, progress_var, progress_bar, status_label, diff_listbox, diff_text, app):
    """
    Compare two SDK directories and update GUI with progress.
    Generates CSV and HTML reports of differences.
    """
    differences = []
    files_added = []
    files_deleted = []
    files_changed = 0
    total_added_lines = 0
    total_removed_lines = 0

    global diffs_by_file, file_status_dict
    diffs_by_file = {}
    file_status_dict = {}

    # Build set of files in old SDK
    old_files_set = set()
    selected_exts = get_selected_extensions()
    for root_dir, _, files in os.walk(old_sdk_path):
        for file in files:
            if file.endswith(selected_exts) or file in ('Makefile', 'Dockerfile'): 
                rel = os.path.relpath(os.path.join(root_dir, file), old_sdk_path)
                old_files_set.add(rel)
    # Build set of files in new SDK
    new_files_set = set()
    for root_dir, _, files in os.walk(new_sdk_path):
        for file in files:
            if file.endswith(selected_exts) or file in ('Makefile', 'Dockerfile'):
                rel = os.path.relpath(os.path.join(root_dir, file), new_sdk_path)
                new_files_set.add(rel)
    # Union of all files for comparison
    all_files = old_files_set.union(new_files_set)
    total_files = len(all_files)
    processed_files = 0

    def update_progress():
        """Update progress bar and status label."""
        progress_bar['value'] = progress_var.get()
        status_label.config(text=f'Processed {processed_files} of {total_files} files')
        status_label.update_idletasks()

    # Compare each file in the union
    for relative_path in sorted(all_files):
        old_file_path = os.path.join(old_sdk_path, relative_path)
        new_file_path = os.path.join(new_sdk_path, relative_path)
        if os.path.exists(old_file_path) and os.path.exists(new_file_path):
            try:
                with open(old_file_path, 'r', encoding='utf-8', errors='ignore') as f1, \
                     open(new_file_path, 'r', encoding='utf-8', errors='ignore') as f2:
                    old_lines = f1.readlines()
                    new_lines = f2.readlines()
                    diff_lines = list(unified_diff(
                        old_lines,
                        new_lines,
                        fromfile=old_file_path,
                        tofile=new_file_path
                    ))
                    if diff_lines:
                        differences.append((relative_path, diff_lines))
                        diffs_by_file[relative_path] = diff_lines
                        file_status_dict[relative_path] = "changed"
                        files_changed += 1
                        removed = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
                        added = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
                        total_removed_lines += removed
                        total_added_lines += added
                    else:
                        file_status_dict[relative_path] = "unchanged"
            except Exception as e:
                file_status_dict[relative_path] = "error"
                print(f"ERROR: Could not process {old_file_path} or {new_file_path}: {e}")
        elif not os.path.exists(old_file_path):
            files_added.append(relative_path)
            file_status_dict[relative_path] = "added"
        elif not os.path.exists(new_file_path):
            files_deleted.append(relative_path)
            file_status_dict[relative_path] = "deleted"
        processed_files += 1
        progress_var.set((processed_files / total_files) * 100)
        update_progress()

    # Write CSV report of differences
    try:
        csv_output = os.path.join(output_dir, 'differences.csv')
        with open(csv_output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['File', 'Differences'])
            for file, diffs in differences:
                diff_text_csv = ''.join(diffs).replace('\n', '\\n')
                writer.writerow([file, diff_text_csv])
    except Exception as e:
        print(f"ERROR: Could not write CSV output: {e}")

    # Write HTML report of differences
    try:
        html_output = os.path.join(output_dir, 'differences.html')
        with open(html_output, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write('''<html><head>
            <style>
            pre {background:#f0f0f0; padding:10px; border:1px solid #ccc; white-space: pre-wrap; font-family: Consolas, monospace;}
            body {font-family: Arial, sans-serif;}
            .instruction {background:#e6f0fa; border:1px solid #7ea6d8; padding:12px; margin-bottom:20px;}
            .summary {background:#dff0d8; border:1px solid #a3c293; padding:12px; margin-bottom:20px;}
            span.keyword {color: blue; font-weight: bold;}
            </style></head><body>
            <h1>SDK Differences Report</h1>
            <div class="instruction">
                <strong>How to read this document:</strong><br>
                - Lines starting with <code>-</code> were present in the OLD SDK but removed or changed.<br>
                - Lines starting with <code>+</code> were added or modified in the NEW SDK.<br>
                - Lines without a prefix provide file context.<br>
                - Files missing or added are listed as separate notices.<br>
                Review changes carefully before updating your code base.
            </div>''')

            htmlfile.write(f'''
            <div class="summary">
                <h2>Summary Report</h2>
                <p><strong>Files Changed:</strong> {files_changed}</p>
                <p><strong>Files Added:</strong> {len(files_added)}</p>
                <p><strong>Files Deleted:</strong> {len(files_deleted)}</p>
                <p><strong>Total Lines Added:</strong> {total_added_lines}</p>
                <p><strong>Total Lines Removed:</strong> {total_removed_lines}</p>
            </div>''')

            if files_added:
                htmlfile.write('<h3>Newly Added Files</h3><ul>')
                for f in files_added:
                    htmlfile.write(f'<li>{escape(f)}</li>')
                htmlfile.write('</ul>')

            if files_deleted:
                htmlfile.write('<h3>Deleted Files</h3><ul>')
                for f in files_deleted:
                    htmlfile.write(f'<li>{escape(f)}</li>')
                htmlfile.write('</ul>')

            for file, diffs in differences:
                htmlfile.write(f'<h2>{escape(file)}</h2><pre>')
                diff_html_text = ''.join(diffs)
                # Highlight keywords in diff output
                for kw in KEYWORDS:
                    diff_html_text = diff_html_text.replace(kw, f'<span class="keyword">{kw}</span>')
                htmlfile.write(diff_html_text)
                htmlfile.write('</pre>')

            htmlfile.write('</body></html>')
    except Exception as e:
        print(f"ERROR: Could not write HTML output: {e}")

    # Update listbox in main thread with changed, added, or deleted files
    def update_listbox():
        diff_listbox.delete(0, tk.END)
        files = [file for file, status in file_status_dict.items() if status in ("changed", "added", "deleted")]
        for file in sorted(files):
            diff_listbox.insert(tk.END, file)
        if files:
            diff_listbox.selection_set(0)
            diff_listbox.event_generate('<<ListboxSelect>>')

    app.after(0, update_listbox)

    return diffs_by_file, files_added, files_deleted, file_status_dict

def run_comparison_thread(old_sdk_entry, new_sdk_entry, output_entry, progress_var, progress_bar, status_label, diff_listbox, diff_text, root):
    """Start SDK comparison in a separate thread."""
    old_sdk_path = old_sdk_entry.get()
    new_sdk_path = new_sdk_entry.get()
    output_dir = output_entry.get()
    if not (os.path.isdir(old_sdk_path) and os.path.isdir(new_sdk_path) and os.path.isdir(output_dir)):
        messagebox.showerror('Error', 'Please select valid directories for all fields.')
        return

    def task():
        global diffs_by_file, files_added, files_deleted, file_status_dict
        diffs_by_file, files_added, files_deleted, file_status_dict = compare_sdk_directories_gui(
            old_sdk_path, new_sdk_path, output_dir, progress_var, progress_bar, status_label, diff_listbox, diff_text, root)
        messagebox.showinfo('Scan Complete', 'SDK comparison completed!')

    threading.Thread(target=task).start()

def drop_event_handler(event, entry_widget):
    """Handle drag-and-drop for directory entry widgets."""
    path = event.data
    if path.startswith('{') and path.endswith('}'):
        path = path[1:-1]
    entry_widget.delete(0, tb.END)
    entry_widget.insert(0, path)

def on_diff_select(evt):
    """Display diff details for selected file in the listbox."""
    selected = diff_listbox.curselection()
    if not selected:
        return
    filename = diff_listbox.get(selected[0])
    status = file_status_dict.get(filename, "")
    diff_lines = diffs_by_file.get(filename)
    diff_text.config(state='normal')
    diff_text.delete('1.0', tk.END)
    if status == "added":
        diff_text.insert(tk.END, "File ADDED. Did not exist in old SDK.")
    elif status == "deleted":
        diff_text.insert(tk.END, "File DELETED. Not present in new SDK.")
    elif status == "changed" and diff_lines:
        for line in diff_lines:
            if line.startswith('+'):
                diff_text.insert(tk.END, line, 'added')
            elif line.startswith('-'):
                diff_text.insert(tk.END, line, 'removed')
            else:
                diff_text.insert(tk.END, line)
    elif status == "error":
        diff_text.insert(tk.END, "Could not process this file due to an error (see console for details).")
    else:
        diff_text.insert(tk.END, "No content changes in this file.")
    diff_text.config(state='disabled')
    diff_text.update()

# --- GUI Setup ---

app = TkinterDnD.Tk()
app.title('SDK Diff Scanner')

frame = tb.Frame(app)
frame.pack(pady=10, padx=10, fill="both", expand=True)

# Old SDK directory selection
old_sdk_label = tb.Label(frame, text='Old SDK Folder:')
old_sdk_label.grid(row=0, column=0, sticky='w')
old_sdk_entry = tb.Entry(frame, width=50)
old_sdk_entry.grid(row=0, column=1)
old_sdk_btn = tb.Button(frame, text='Browse', bootstyle="success-outline", width=10,
                        command=lambda: old_sdk_entry.delete(0, tb.END) or old_sdk_entry.insert(0, filedialog.askdirectory()))
old_sdk_btn.grid(row=0, column=2)

# New SDK directory selection
new_sdk_label = tb.Label(frame, text='New SDK Folder:')
new_sdk_label.grid(row=1, column=0, sticky='w')
new_sdk_entry = tb.Entry(frame, width=50)
new_sdk_entry.grid(row=1, column=1)
new_sdk_btn = tb.Button(frame, text='Browse', bootstyle="info-outline", width=10,
                        command=lambda: new_sdk_entry.delete(0, tb.END) or new_sdk_entry.insert(0, filedialog.askdirectory()))
new_sdk_btn.grid(row=1, column=2)

# Output directory selection
output_label = tb.Label(frame, text='Output Folder:')
output_label.grid(row=2, column=0, sticky='w')
output_entry = tb.Entry(frame, width=50)
output_entry.grid(row=2, column=1)
output_btn = tb.Button(frame, text='Browse', bootstyle="secondary-outline", width=10,
                       command=lambda: output_entry.delete(0, tb.END) or output_entry.insert(0, filedialog.askdirectory()))
output_btn.grid(row=2, column=2)

# Save/load config buttons
save_btn = tb.Button(frame, text='Save Config', bootstyle="success", width=12,
                     command=lambda: save_config(old_sdk_entry.get(), new_sdk_entry.get(), output_entry.get()))
save_btn.grid(row=3, column=0, pady=10)

load_btn = tb.Button(frame, text='Load Config', bootstyle="info", width=12)
load_btn.grid(row=3, column=1, pady=10)

def on_load_click():
    """Load config and populate entry fields."""
    config = load_config()
    old_sdk_entry.delete(0, tb.END)
    old_sdk_entry.insert(0, config.get("old_sdk_path", ""))
    new_sdk_entry.delete(0, tb.END)
    new_sdk_entry.insert(0, config.get("new_sdk_path", ""))
    output_entry.delete(0, tb.END)
    output_entry.insert(0, config.get("output_dir", ""))

load_btn.configure(command=on_load_click)

# Extension selection checkboxes
ext_frame = tb.LabelFrame(frame, text="File types to scan")
ext_frame.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky='we')
col = 0
row = 0
for ext, label in EXTENSION_OPTIONS:
    var = tk.BooleanVar(value=(ext in ('.c', '.h')))
    cb = tb.Checkbutton(ext_frame, text=label, variable=var)
    cb.grid(row=row, column=col, sticky='w', padx=4)
    ext_vars[ext] = var
    col += 1
    if col % 6 == 0:
        row += 1
        col = 0

# Progress bar and status label
progress_var = tb.DoubleVar()
progress_bar = tb.Progressbar(frame, variable=progress_var, maximum=100, bootstyle="striped-info", length=380)
progress_bar.grid(row=4, column=0, columnspan=3, sticky='we', pady=15)

status_label = tb.Label(frame, text='Select SDK folders and output folder, then start the scan.', anchor='center')
status_label.grid(row=5, column=0, columnspan=3)

# Listbox for files with differences
diff_listbox = tk.Listbox(frame, height=10, exportselection=False)
diff_listbox.grid(row=7, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
diff_listbox.bind('<<ListboxSelect>>', on_diff_select)

# Text area for diff details
diff_text = scrolledtext.ScrolledText(frame, wrap=tk.NONE, height=20)
diff_text.grid(row=8, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
diff_text.tag_config('added', foreground='green')
diff_text.tag_config('removed', foreground='red')

frame.grid_rowconfigure(7, weight=1)
frame.grid_rowconfigure(8, weight=3)
frame.grid_columnconfigure(1, weight=1)

diff_listbox.bind('<<ListboxSelect>>', on_diff_select)

# Enable drag-and-drop for entry widgets
old_sdk_entry.drop_target_register(DND_FILES)
old_sdk_entry.dnd_bind('<<Drop>>', lambda e: drop_event_handler(e, old_sdk_entry))

new_sdk_entry.drop_target_register(DND_FILES)
new_sdk_entry.dnd_bind('<<Drop>>', lambda e: drop_event_handler(e, new_sdk_entry))

output_entry.drop_target_register(DND_FILES)
output_entry.dnd_bind('<<Drop>>', lambda e: drop_event_handler(e, output_entry))

# Start scan button
start_btn = tb.Button(
    frame, text='Start Scan',
    bootstyle="primary", width=25,
    command=lambda: run_comparison_thread(
        old_sdk_entry, new_sdk_entry, output_entry,
        progress_var, progress_bar, status_label, diff_listbox, diff_text, app
    )
)
start_btn.grid(row=6, column=0, columnspan=3, pady=5)

# Set minimum window size
app.update()
app.minsize(app.winfo_width(), app.winfo_height())

# Start main event loop
app.mainloop()
