from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib
import os
import shutil
import sqlite3
import json

from file_tools import scan_folder, organize_files, get_file_type, format_size

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "organizer.db"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-key-change-me")


def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder TEXT NOT NULL,
                scanned_at TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                duplicate_groups INTEGER NOT NULL,
                total_bytes INTEGER NOT NULL
            )
        """)


def save_scan(folder, summary):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO scan_history(folder, scanned_at, file_count, duplicate_groups, total_bytes) VALUES (?, ?, ?, ?, ?)",
            (folder, datetime.now().isoformat(timespec="seconds"), summary["file_count"],
             summary["duplicate_group_count"], summary["total_bytes"])
        )


def build_dashboard(folder, records, duplicate_groups, errors=None):
    ext_counts = Counter((r["extension"] or "No extension").upper() for r in records)
    type_counts = Counter(r["file_type"] for r in records)
    total_bytes = sum(r["size_bytes"] for r in records)
    duplicate_bytes = sum(
        max(0, group["total_bytes"] - group["size_bytes"])
        for group in duplicate_groups
    )
    summary = {
        "file_count": len(records),
        "folder_count": len({str(Path(r["path"]).parent) for r in records}),
        "total_bytes": total_bytes,
        "total_size": format_size(total_bytes),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_file_count": sum(len(g["files"]) - 1 for g in duplicate_groups),
        "duplicate_bytes": duplicate_bytes,
        "duplicate_size": format_size(duplicate_bytes),
    }
    return {
        "folder": folder,
        "records": records,
        "duplicate_groups": duplicate_groups,
        "summary": summary,
        "extension_labels": list(ext_counts.keys())[:12],
        "extension_values": list(ext_counts.values())[:12],
        "type_labels": list(type_counts.keys()),
        "type_values": list(type_counts.values()),
        "errors": errors or [],
    }


@app.route("/", methods=["GET", "POST"])
def index():
    folder = ""
    records = []
    duplicate_groups = []
    errors = []
    if request.method == "POST":
        folder = request.form.get("folder", "").strip()
        if not folder:
            flash("Enter a folder path to scan.", "error")
        else:
            try:
                records, duplicate_groups, errors = scan_folder(folder)
                summary = {
                    "file_count": len(records),
                    "duplicate_group_count": len(duplicate_groups),
                    "total_bytes": sum(r["size_bytes"] for r in records),
                }
                save_scan(str(Path(folder).expanduser().resolve()), summary)
                flash(f"Scan complete: {len(records)} files checked.", "success")
            except (OSError, ValueError) as exc:
                flash(str(exc), "error")
    dashboard = build_dashboard(folder, records, duplicate_groups, errors)
    return render_template("index.html", **dashboard)


@app.post("/organize")
def organize():
    folder = request.form.get("folder", "").strip()
    mode = request.form.get("mode", "dry-run")
    if not folder:
        flash("Enter a folder path first.", "error")
        return redirect(url_for("index"))
    try:
        result = organize_files(folder, dry_run=(mode != "execute"))
        if mode == "execute":
            flash(f"Organization complete: moved {result['moved']} files.", "success")
        else:
            flash(f"Preview ready: {result['planned']} files would be organized. No files were moved.", "success")
        return render_template("organize.html", folder=folder, result=result, dry_run=(mode != "execute"))
    except (OSError, ValueError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))


@app.get("/history")
def history():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM scan_history ORDER BY id DESC LIMIT 25").fetchall()
    return render_template("history.html", rows=rows)


@app.get("/api/scan")
def api_scan():
    folder = request.args.get("folder", "").strip()
    if not folder:
        return jsonify({"error": "folder query parameter is required"}), 400
    try:
        records, duplicates, errors = scan_folder(folder)
        return jsonify({
            "folder": str(Path(folder).expanduser().resolve()),
            "file_count": len(records),
            "duplicate_groups": duplicates,
            "errors": errors,
            "files": records,
        })
    except (OSError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


init_db()

if __name__ == "__main__":
    # Local-only server by default. Do not expose this file-management app to a public network.
    app.run(host="127.0.0.1", port=6969, debug=False)
