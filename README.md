# File Organizer and Duplicate File Detection Tool

A local Flask web application that scans a folder, finds exact duplicate files using SHA-256, summarizes file types, and organizes top-level files into category folders.

## Features
- Dashboard with file count, total size, duplicate groups, and estimated duplicate storage.
- File-type and extension charts.
- Exact duplicate detection using SHA-256 plus file size.
- Organization preview before moving anything.
- Category folders: Images, Documents, Audio, Video, Archives, Code, and Other.
- Collision-safe moves: existing files are not overwritten.
- Scan history stored in SQLite.
- JSON endpoint at `/api/scan?folder=PATH`.
- Unit tests for duplicate detection and organization preview.

## Requirements
- Python 3.10+
- Windows, macOS, or Linux
- Flask (install from `requirements.txt`)

## Setup
1. Extract the ZIP.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000`.

## How to use
1. Enter the full path of a folder you own or have permission to access.
2. Select **Scan folder** to calculate file hashes and view duplicates.
3. Open **Organize files** and review the preview first.
4. Choose **Execute organization** only after reviewing the destinations.
5. Use **History** to see recent scan summaries.

## Important safety notes
- Run locally; do not expose the server to the public internet.
- Start with a test folder containing copies of files.
- Organization moves only files directly inside the chosen folder. It does not recursively move files from nested folders.
- Scanning is recursive and reads file contents to compute SHA-256 hashes.
- Duplicate detection identifies exact byte-for-byte copies, not visually similar images or files with different metadata/content.
- The app does not automatically delete duplicate files.
- Keep a backup before moving important files.

## Tests
Run `python -m unittest discover -s tests -v`.

## Project structure
```text
File_Organizer_Duplicate_Detection_Tool/
├── app.py
├── file_tools.py
├── requirements.txt
├── README.md
├── report.pdf
├── presentation.pptx
├── templates/
│   ├── index.html
│   ├── organize.html
│   └── history.html
├── static/
│   ├── style.css
│   └── dashboard.js
└── tests/
    └── test_file_tools.py
```
