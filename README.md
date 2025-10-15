# SDK-Difference-Scanner
SDK Diff Scanner is a user-friendly desktop app that compares two SDK directories to find changed, added, or deleted files. It highlights line-by-line differences with color codes, supports custom file type selection, drag-and-drop, and generates detailed HTML and CSV reports for easy review.

## Overview

SDK Diff Scanner is a desktop GUI application designed to compare two Software Development Kit (SDK) directories. It identifies differences in source, header, and configuration files and highlights changes, additions, and deletions in a user-friendly interface. The application supports drag-and-drop, customizable file type filtering, and generates detailed reports in CSV and HTML formats.

## Features

- Compare SDK directories to detect differences in files.
- Supports common programming languages and config file extensions, user-selectable.
- Interactive diff viewer showing line-by-line changes with color coding.
- Highlights added, deleted, and changed files separately.
- Drag-and-drop support for folder selection.
- Save and Load configuration for directories.
- Progress bar and status display during scanning.
- Export differences as CSV and a well-formatted HTML report.
- Lightweight GUI built with Tkinter, ttkbootstrap, and tkinterdnd2.


## Requirements

- Python 3.8 or higher
- Dependencies:
    - ttkbootstrap
    - tkinterdnd2
    - Tkinter (usually included with Python)

Install dependencies using pip:

```
pip install ttkbootstrap tkinterdnd2
```


## Usage

### Running the Application

```bash
python sdk_diff_scanner.py
```


### GUI Controls

- **Old SDK Folder, New SDK Folder**: Select directories to compare.
- **Output Folder**: Select folder where reports will be saved.
- **File types to scan**: Select which file extensions to include in comparison.
- **Save Config**: Save current folder selections for reuse.
- **Load Config**: Load saved configuration.
- **Start Scan**: Begin scanning and comparison.
- **File List (Top Box)**: Files that have changes, additions, or deletions. Select to view details.
- **Diff Viewer (Bottom Box)**: Shows detailed line differences or status message for selected file.
- Progress bar and status label indicate scan progress.


### Example Workflow:

1. Launch the app.
2. Select your old SDK directory and new SDK directory.
3. Choose an output folder.
4. Optionally select file types to include in the scan.
5. Click "Start Scan".
6. View changed/added/deleted files in the list.
7. Click on any file to see line-by-line differences.
8. Examine the saved CSV and HTML reports in the output directory.

## Capabilities and Limitations

### Supported file types

By default, common source code and config extensions are supported (e.g., `.c`, `.h`, `.py`, `.cfg`, `.json`). File types can be customized before scanning.

### Comparison

- Performs line-based text comparison.
- Does not support binary file diffs (e.g., `.bin`, `.a`).
- Handles large SDK directories with progress feedback.


### Reports

- CSV report includes filename and encoded diff text.
- HTML report includes colored syntax, summaries, and explanations.
- Both reports saved in the specified output directory.


## Contributing

Contributions are welcome! Please submit issues or pull requests for bug fixes or feature enhancements.

## License

MIT License

***

For further information or troubleshooting, please open an issue or contact the maintainer.

