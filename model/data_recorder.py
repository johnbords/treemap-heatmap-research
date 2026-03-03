import os
import sys
import csv
from typing import List, Optional

class FilePathConfig:
    @staticmethod
    def _set_file_path(strip_count) -> str:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            stripped_file_path = os.path.dirname(os.path.abspath(__file__))
            for i in range(0, strip_count):
                stripped_file_path = os.path.dirname(stripped_file_path)
            return stripped_file_path

    @staticmethod
    def generate_complete_file_path(folder_name="", file_name="", strip_count=0) -> str:
        file_path = FilePathConfig._set_file_path(strip_count)
        return os.path.join(file_path, folder_name, file_name)


def _resolve_path(path: str) -> str:
    """If a relative path is provided, resolve it beside the .exe (PyInstaller) or beside this module."""
    if not path:
        return path
    if os.path.isabs(path):
        return path
    base = FilePathConfig._set_file_path(strip_count=0)
    return os.path.join(base, path)



def _headers(total_trials: int):
    cols = ["Participant ID"]
    for i in range(1, total_trials + 1):
        cols.append(f"Trial {i} Time")
        cols.append(f"Trial {i} Errors")
    return cols


def ensure_workbook(file_path: str, total_trials: int):
    """
    For CSV, we just ensure the directory exists.
    Header will be written automatically if file doesn't exist.
    """
    file_path = _resolve_path(file_path)
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)


def get_next_participant_id(file_path: str) -> int:
    file_path = _resolve_path(file_path)
    """
    Reads CSV and returns max participant_id + 1
    """
    file_path = _resolve_path(file_path)
    if not os.path.exists(file_path):
        return 1

    ids = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if row and row[0]:
                try:
                    ids.append(int(row[0]))
                except Exception:
                    pass

    return max(ids) + 1 if ids else 1


def append_participant_result(
    file_path: str,
    participant_id: int,
    trial_times: List[Optional[float]],
    trial_errors: List[int],
):
    file_path = _resolve_path(file_path)
    """
    Append one row safely to CSV.
    No file locking issues.
    """
    file_exists = os.path.exists(file_path)

    header = _headers(len(trial_times))

    row = [participant_id]
    for t, e in zip(trial_times, trial_errors):
        row.append("" if t is None else float(t))
        row.append(int(e))

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(header)

        writer.writerow(row)