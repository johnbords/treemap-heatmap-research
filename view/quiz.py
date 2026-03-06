import os
import sys
import uuid
import csv
import re
import time
from typing import List, Optional

import streamlit as st
from streamlit_scroll_to_top import scroll_to_here

from view import js_timer_component  # your existing JS timer component


# ---------------------------
# File path helper (PyInstaller-safe)
# Writes/reads results beside the packaged .exe (or beside this file when running as scripts).
# ---------------------------
class FilePathConfig:

    @staticmethod
    def _set_file_path(strip_count) -> str:
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # When bundled with PyInstaller, sys._MEIPASS is the temp folder
            stripped_file_path = os.path.dirname(sys.executable)
            return stripped_file_path
        else:  # If running as a python script
            stripped_file_path = os.path.dirname(os.path.abspath(__file__))
            # Strips folder level incrementally
            for _ in range(0, strip_count):
                stripped_file_path = os.path.dirname(stripped_file_path)
            return stripped_file_path

    @staticmethod
    def generate_complete_file_path(folder_name="", file_name="", strip_count=0) -> str:
        file_path = FilePathConfig._set_file_path(strip_count)
        return os.path.join(file_path, folder_name, file_name)


# ---------------------------
# Config
# ---------------------------
QUIZ_COLOR = "#32cd32"
FADE_SECONDS = 0.5

RESULTS_DIR = FilePathConfig.generate_complete_file_path(folder_name="results", strip_count=0)

# ---------------------------
# Year filter override (driven by question text)
# Convention (recommended):
#   Single year: "In the year XXXX, ..."
#   Range:       "From XXXX to YYYY, ..."
# We also support some legacy variants ("In 2000", "Between 1999 and 2002") as fallback.
# ---------------------------
_SINGLE_YEAR_RE = re.compile(r"\bIn\s+the\s+year\s+(\d{4})\b", re.IGNORECASE)
_SINGLE_YEAR_FALLBACK_RE = re.compile(r"\bIn\s+(\d{4})\b", re.IGNORECASE)

_RANGE_FROM_TO_RE = re.compile(r"\bFrom\s+(\d{4})\s+to\s+(\d{4})\b", re.IGNORECASE)
_RANGE_BETWEEN_AND_RE = re.compile(r"\bBetween\s+(\d{4})\s+and\s+(\d{4})\b", re.IGNORECASE)


def _parse_year_override(question_text: str):
    """Return dict like {mode: 'single', year: 2000} or {mode:'range', from:1999, to:2002} or None."""
    if not question_text:
        return None

    # Remove leading numbering like "3) "
    q = re.sub(r"^\s*\d+\)\s*", "", str(question_text)).strip()

    m = _RANGE_FROM_TO_RE.search(q) or _RANGE_BETWEEN_AND_RE.search(q)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        lo, hi = (y1, y2) if y1 <= y2 else (y2, y1)
        return {"mode": "range", "from": lo, "to": hi}

    m = _SINGLE_YEAR_RE.search(q) or _SINGLE_YEAR_FALLBACK_RE.search(q)
    if m:
        y = int(m.group(1))
        return {"mode": "single", "year": y}

    return None


def _clear_year_override():
    st.session_state.year_filter_override = None


def _set_year_override_from_question(question_text: str):
    st.session_state.year_filter_override = _parse_year_override(question_text)


# ---------------------------
# Practice Questions (UNTIMED)
# ---------------------------
PRACTICE_QUESTIONS = [
    {
        "q": "1) In the year 2001, which genre, from the list below, is more popular?\n\nRock, Country (2001)",
        "choices": ["Rock", "Country"],
        "correct": 1,
    },
    {
        "q": "2) In the year 2003, which genre has the highest popularity?\n\nRock, Dance/Electronic, Latin, Country (Year 2003)",
        "choices": ["Rock", "Dance/Electronic", "Latin", "Country"],
        "correct": 2,
    },
    {
        "q": "3) In the year 2020, what is the average popularity value of the genre 'World/Traditional'?\n\nWorld/Traditional (Year 2020)",
        "choices": ["45.6", "52.1", "57.0", "68.9"],
        "correct": 2,
    },
]
PRACTICE_TOTAL = len(PRACTICE_QUESTIONS)


# ---------------------------
# Main Questions (TIMED)
# ---------------------------
QUESTIONS = [

    # -------------------------
    # Set 1
    # -------------------------

    {"q": "1) In the year 1999, which genre has higher popularity? Hip Hop or Pop?\n\nHip Hop vs Pop (Year 1999)",
     "choices": ["Hip Hop", "Pop"],
     "correct": 0},  # Answer: Hip Hop

    {"q": "2) In the year 2000, which genre, from the list below, has the second highest popularity?\n\nHip Hop, Metal, Pop, R&B (Year 2000)",
     "choices": ["Hip Hop", "Metal", "Pop", "R&B"],
     "correct": 2},  # Answer: Pop

    {"q": "3) In the year 2000, which genre, from the list below, has the lowest popularity?\n\nHip Hop, Metal, Pop, R&B (Year 2000)",
     "choices": ["Hip Hop", "Metal", "Pop", "R&B"],
     "correct": 3},  # Answer: R&B

    {"q": "4) From 1999 to 2002, in which year does R&B have the lowest average popularity value?\n\nR&B (1999–2002)",
     "choices": ["1999", "2000", "2001", "2002"],
     "correct": 1},  # Answer: 2000

    # -------------------------
    # Set 2
    # -------------------------

    {
        "q": "5) In the year 2007, which genre, from the list below, has the second highest popularity?\n\nDance-Electronic, Jazz, Latin, Rock (Year 2007)",
        "choices": ["Dance/Electronic", "Jazz", "Latin", "Rock"],
        "correct": 0},  # Answer: Dance/Electronic

    {"q": "6) In the year 2006, what is the average popularity value of Rock?\n\nRock (Year 2006)",
     "choices": ["45.6", "42.0", "67.9", "68.1"],
     "correct": 2},  # Answer: 67.9

    {"q": "7) From 2003 to 2007, in which year does Latin have the highest average popularity value?\n\nLatin (2003–2007)",
     "choices": ["2003", "2004", "2005", "2006", "2007"],
     "correct": 3},  # Answer: 2006

    {"q": "8) In the year 2004, which genre, from the list below, is missing?\n\nDance-Electronic, Jazz, Latin, Rock (Year 2004)",
     "choices": ["Dance/Electronic", "Jazz", "Latin", "Rock"],
     "correct": 1},  # Answer: Jazz

    # -------------------------
    # Set 3
    # -------------------------

    {
        "q": "9) From 2008 to 2012, in which year does the genre 'Country' have the lowest average popularity value?\n\nCountry (2008–2012)",
        "choices": ["2008", "2009", "2010", "2011", "2012"],
        "correct": 4},  # Answer: 2012

    {"q": "10) In the year 2012, what is the average popularity value of the genre 'Folk/Acoustic?'\n\nFolk/Acoustic (Year 2012)",
     "choices": ["75.5", "76.9", "77.1", "79.0"],
     "correct": 3}  # Answer: 79.0
]

TOTAL_QUESTIONS = len(QUESTIONS)


# ============================================================
# Datamap -> file path
# ============================================================
def _datamap_suffix() -> str:
    """
    Uses your state_controller.py session state key:
      st.session_state.chart_type_radio == "Heatmap" or "Treemap"
    """
    chart = st.session_state.get("chart_type_radio", "Heatmap")  # "Heatmap" | "Treemap"
    return str(chart).strip().lower()  # "heatmap" | "treemap"


def _results_csv_path() -> str:
    suffix = _datamap_suffix()
    return os.path.join(RESULTS_DIR, f"performance_{suffix}.csv")


def _results_xlsx_path_from_csv(csv_path: str) -> str:
    base, _ = os.path.splitext(csv_path)
    return base + ".xlsx"


# ============================================================
# CSV helpers
# ============================================================
def _headers(total_trials: int) -> List[str]:
    cols = ["Participant ID"]
    for i in range(1, total_trials + 1):
        cols.append(f"Trial {i} Time")
        cols.append(f"Trial {i} Errors")
    return cols


def ensure_csv_file(csv_path: str, total_trials: int) -> None:
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    if os.path.exists(csv_path):
        return

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_headers(total_trials))


def get_next_participant_id(csv_path: str) -> int:
    if not os.path.exists(csv_path):
        return 1

    ids: List[int] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        next(r, None)  # header
        for row in r:
            if not row:
                continue
            try:
                ids.append(int(row[0]))
            except Exception:
                continue

    return (max(ids) + 1) if ids else 1


def append_participant_result_csv(
    csv_path: str,
    participant_id: int,
    trial_times: List[Optional[float]],
    trial_errors: List[int],
) -> None:
    if len(trial_times) != len(trial_errors):
        raise ValueError("trial_times and trial_errors must be the same length")

    row = [participant_id]
    for t, e in zip(trial_times, trial_errors):
        row.append("" if t is None else float(t))
        row.append(int(e))

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(row)


def is_workbook_open_or_locked(path: str) -> bool:
    """
    Returns True if the target XLSX is likely open/locked (Excel commonly locks files on Windows).
    Cross-platform best-effort:
      - Windows: try opening + exclusive byte-range lock via msvcrt
      - Unix: try flock exclusive non-blocking
    """
    if not path or not os.path.exists(path):
        return False

    try:
        # If the OS denies opening for write at all, it's locked.
        f = open(path, "a")
    except PermissionError:
        return True
    except Exception:
        # Unknown edge case; assume not locked to avoid false positives.
        return False

    try:
        if os.name == "nt":
            import msvcrt
            try:
                # lock 1 byte non-blocking
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                return False
            except OSError:
                return True
        else:
            import fcntl
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            except BlockingIOError:
                return True
            except OSError:
                return True
    finally:
        try:
            f.close()
        except Exception:
            pass


# ============================================================
# CSV -> XLSX conversion (after EACH participant run)
# ============================================================
def convert_csv_to_xlsx(csv_path: str) -> str:
    """
    Rebuilds XLSX from the CSV on every participant completion.
    This avoids in-place editing of an existing workbook (simpler + safer).
    If the XLSX is open in Excel, Windows will lock it and this can fail.
    """
    from openpyxl import Workbook

    xlsx_path = _results_xlsx_path_from_csv(csv_path)
    tmp_path = xlsx_path + ".tmp"

    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        for row in r:
            ws.append(row)

    wb.save(tmp_path)
    wb.close()

    os.replace(tmp_path, xlsx_path)
    return xlsx_path


# ============================================================
# UI helpers
# ============================================================
def flash_css():
    if st.session_state.quiz_flash_id <= 0:
        return

    anim = f"quizFade_{st.session_state.quiz_flash_id}"

    st.markdown(
        f"""
        <style>
        @keyframes {anim} {{
          0%   {{ color: {QUIZ_COLOR}; }}
          100% {{ color: #31333f; }}
        }}

        [data-testid="stSidebar"] .quiz-q,
        [data-testid="stSidebar"] .quiz-q * {{
          animation: {anim} {FADE_SECONDS}s ease-out 0s 1;
        }}

        [data-testid="stSidebar"] div[data-testid="stButton"] button,
        [data-testid="stSidebar"] div[data-testid="stButton"] button * {{
          animation: {anim} {FADE_SECONDS}s ease-out 0s 1;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sum_correct_answers() -> int:
    """Number of correct answers among answers actually given."""
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        if QUESTIONS[i]["correct"] == ans
    )


def sum_wrong_answers() -> int:
    """Number of wrong answers among answers actually given."""
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        if QUESTIONS[i]["correct"] != ans
    )


# ============================================================
# Quiz flow helpers
# ============================================================
def reset_quiz():
    st.session_state.quiz_q_idx = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_flash_id += 1

    st.session_state.trial_times = []
    st.session_state.trial_errors = []
    st.session_state.saved_to_disk = False
    st.session_state.converted_to_xlsx = False

    # input lock (debounce) per question
    st.session_state.quiz_input_locked = False

    # timer state
    st.session_state.quiz_handled_done_run_id = None


def reset_practice():
    st.session_state.practice_q_idx = 0
    st.session_state.practice_answers = []


def _prepare_participant_run():
    """
    Prepare run artifacts (CSV path, participant id) ONCE when Start is clicked.
    This keeps the participant id stable through: Practice -> Get ready -> Main quiz.
    """
    csv_path = _results_csv_path()
    st.session_state.results_csv_path = csv_path

    ensure_csv_file(csv_path, TOTAL_QUESTIONS)
    st.session_state.participant_id = get_next_participant_id(csv_path)

    st.session_state.run_prepared = True


def _begin_get_ready_phase():
    st.session_state.quiz_phase = "get_ready"
    reset_quiz()

    st.session_state.quiz_ready_key = f"quiz_ready_timer_{uuid.uuid4()}"
    st.session_state.quiz_ready_run_id = str(uuid.uuid4())
    st.rerun()


def start_flow():
    """
    Sequence:
      Start button -> Practice quiz (untimed) -> Get ready phase -> Main questions (timed)
    """
    _prepare_participant_run()

    st.session_state.quiz_started = True
    st.session_state.quiz_phase = "practice"
    reset_practice()

    st.rerun()


def choose(choice_idx: int):
    # Record answer and advance. Timing is handled outside (on click).
    st.session_state.quiz_answers.append(choice_idx)
    st.session_state.quiz_q_idx += 1
    st.session_state.quiz_flash_id += 1

    # Mark that the next question needs a fresh start timestamp
    st.session_state.quiz_q_start_for_idx = None


def ensure_question_state_for_current_idx():
    """Initialize per-question state once when quiz_q_idx changes."""
    cur = st.session_state.quiz_q_idx
    if st.session_state.get("quiz_q_start_for_idx") != cur:
        st.session_state.quiz_q_start_for_idx = cur
        st.session_state.quiz_q_start_ts = time.time()

        # unlock inputs for the new question
        st.session_state.quiz_input_locked = False


def _record_trial(elapsed: Optional[float], error: int) -> None:
    st.session_state.trial_times.append(None if elapsed is None else float(elapsed))
    st.session_state.trial_errors.append(int(error))


def _save_and_convert_if_needed():
    """
    After ONE participant completes the quiz:
      1) append row to CSV (fast + safe)
      2) convert the CSV -> XLSX (rebuild workbook each time)
    """
    if st.session_state.saved_to_disk:
        return

    st.session_state.saved_to_disk = True  # prevent rerun loops

    csv_path = st.session_state.get("results_csv_path") or _results_csv_path()

    # 1) Save row to CSV
    append_participant_result_csv(
        csv_path,
        st.session_state.participant_id,
        st.session_state.trial_times,
        st.session_state.trial_errors,
    )

    # 2) Convert CSV -> XLSX (after each participant)
    xlsx_path = _results_xlsx_path_from_csv(csv_path)

    # proactively detect Excel lock/open workbook
    if is_workbook_open_or_locked(xlsx_path):
        st.session_state.converted_to_xlsx = False
        st.session_state.results_xlsx_path = xlsx_path
        st.session_state.xlsx_open = True
        st.warning(
            "Saved to CSV, but the XLSX looks OPEN/LOCKED (probably open in Excel).\n"
            "Close the XLSX file, then the next participant will update it."
        )
        return

    try:
        xlsx_path = convert_csv_to_xlsx(csv_path)
        st.session_state.converted_to_xlsx = True
        st.session_state.results_xlsx_path = xlsx_path
        st.session_state.xlsx_open = False
    except PermissionError:
        st.session_state.converted_to_xlsx = False
        st.session_state.results_xlsx_path = xlsx_path
        st.session_state.xlsx_open = True
        st.warning(
            "Saved to CSV, but could not update the XLSX because it is likely open in Excel.\n"
            "Close the XLSX file, then the next participant will update it."
        )


def _is_file_locked(path: str) -> bool:
    """
    Best-effort lock check:
    - Windows: tries a non-blocking 1-byte lock via msvcrt
    - Unix: tries flock non-blocking
    Returns True if the file exists and appears locked/open (e.g., open in Excel).
    """
    if not path or not os.path.exists(path):
        return False

    try:
        f = open(path, "a")
    except PermissionError:
        return True
    except Exception:
        return False

    try:
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                return False
            except OSError:
                return True
        else:
            import fcntl
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            except (BlockingIOError, OSError):
                return True
    finally:
        try:
            f.close()
        except Exception:
            pass


def _check_results_files_unlocked_or_warn() -> bool:
    csv_path = _results_csv_path()
    xlsx_path = _results_xlsx_path_from_csv(csv_path)

    if _is_file_locked(csv_path) or _is_file_locked(xlsx_path):
        st.warning(
            "⚠️ Your results file is currently OPEN (CSV/XLSX).\n\n"
            "Please close it first, then reload the page (F5) before starting."
        )
        return False

    return True


# ============================================================
# Practice render (UNTIMED)
# ============================================================
def _render_practice_sidebar():
    st.header("Practice Questions")

    # finished -> automatically go to Get Ready
    if st.session_state.practice_q_idx >= PRACTICE_TOTAL:
        _clear_year_override()
        st.success("Practice complete. Starting the main quiz...")
        _begin_get_ready_phase()
        return

    q_idx = st.session_state.practice_q_idx
    q = PRACTICE_QUESTIONS[q_idx]

    q_text = q["q"].split("\n\n")
    main = q_text[0]
    focus = q_text[1] if len(q_text) > 1 else ""

    _set_year_override_from_question(main)

    st.markdown(
        f"""
        <div class='quiz-q'>
            <b>{main}</b>
            <br><br>
            <div style='text-align:center; font-weight:bold; font-size:18px;'>
                {focus}
            </div>
            <br>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Question {q_idx + 1} / {PRACTICE_TOTAL}")

    for i, text in enumerate(q["choices"]):
        if st.button(text, key=f"practice_choice_{q_idx}_{i}", width='stretch'):
            st.session_state.practice_answers.append(i)
            st.session_state.practice_q_idx += 1

            # optional: autoscroll to top for the next question
            st.session_state.quiz_scroll_ticks = 2
            st.rerun()


# ============================================================
# Main render
# ============================================================
def render_quiz():
    # ---------------------------
    # State init
    # ---------------------------
    st.session_state.setdefault("quiz_started", False)
    st.session_state.setdefault("quiz_phase", "idle")  # idle|practice|get_ready|quiz

    st.session_state.setdefault("run_prepared", False)
    st.session_state.setdefault("participant_id", None)

    # practice state
    st.session_state.setdefault("practice_q_idx", 0)
    st.session_state.setdefault("practice_answers", [])

    # main quiz state
    st.session_state.setdefault("quiz_q_idx", 0)
    st.session_state.setdefault("quiz_answers", [])
    st.session_state.setdefault("quiz_flash_id", 0)

    st.session_state.setdefault("quiz_ready_key", f"quiz_ready_timer_{uuid.uuid4()}")
    st.session_state.setdefault("quiz_ready_run_id", str(uuid.uuid4()))

    st.session_state.setdefault("trial_times", [])
    st.session_state.setdefault("trial_errors", [])
    st.session_state.setdefault("saved_to_disk", False)
    st.session_state.setdefault("converted_to_xlsx", False)

    st.session_state.setdefault("quiz_input_locked", False)
    st.session_state.setdefault("quiz_scroll_ticks", 0)
    st.session_state.setdefault("quiz_q_start_ts", None)
    st.session_state.setdefault("quiz_q_start_for_idx", None)

    st.session_state.setdefault("results_csv_path", None)
    st.session_state.setdefault("results_xlsx_path", None)
    st.session_state.setdefault("xlsx_open", False)

    # --- Autoscroll to top (render for 2 reruns for reliability) ---
    if st.session_state.get("quiz_scroll_ticks", 0) > 0:
        scroll_to_here(0, key=f"quiz_scroll_{uuid.uuid4()}")
        st.session_state.quiz_scroll_ticks -= 1

    with st.sidebar:
        st.header("Quiz")

        # ------------------------------------------------------------
        # Idle (Start)
        # ------------------------------------------------------------
        if not st.session_state.quiz_started or st.session_state.quiz_phase == "idle":
            _clear_year_override()
            st.info("Click **Start** to begin.")

            if st.button("Start", key="quiz_start", width='stretch'):
                # Check locks BEFORE starting / creating files / assigning participant id
                if not _check_results_files_unlocked_or_warn():
                    st.stop()

                start_flow()

            return

        # ------------------------------------------------------------
        # Practice (UNTIMED)
        # ------------------------------------------------------------
        if st.session_state.quiz_phase == "practice":
            _render_practice_sidebar()
            return

        # ------------------------------------------------------------
        # Get Ready
        # ------------------------------------------------------------
        if st.session_state.quiz_phase == "get_ready":
            _clear_year_override()
            st.markdown(
                "<h1 style='font-size:30px; text-align:center;'>Get Ready!</h1>",
                unsafe_allow_html=True,
            )

            ready_style = dict(js_timer_component.TIMER_STYLE)
            ready_style["show_bar"] = False
            ready_style["seconds_only"] = True
            ready_style["align"] = "center"
            ready_style["font_size"] = "80px"
            ready_style["font_color"] = "#31333f"

            result, _ = js_timer_component.countdown(
                3,
                key=st.session_state.quiz_ready_key,
                run_id=st.session_state.quiz_ready_run_id,
                style=ready_style,
            )

            done = (result or {}).get("done")
            if done and done.get("finished") is True:
                st.session_state.quiz_phase = "quiz"
                st.rerun()
            return

        # ------------------------------------------------------------
        # Finished (AUTO SAVE + AUTO CONVERT AFTER 1 PARTICIPANT)
        # ------------------------------------------------------------
        if st.session_state.quiz_q_idx >= TOTAL_QUESTIONS:
            _clear_year_override()
            _save_and_convert_if_needed()

            flash_css()
            st.success("Quiz finished!")

            chart = st.session_state.get("chart_type_radio", "Heatmap")
            # st.write(f"Participant ID: **{st.session_state.participant_id}**")
            st.write(f"Datamap: **{chart}**")
            # st.write(f"CSV: `{st.session_state.get('results_csv_path') or _results_csv_path()}`")

            xlsx_path = st.session_state.get("results_xlsx_path") or _results_xlsx_path_from_csv(
                st.session_state.get("results_csv_path") or _results_csv_path()
            )
            # st.write(f"XLSX: `{xlsx_path}`")

            # if st.session_state.converted_to_xlsx:
            #     st.caption("✅ XLSX updated after this participant.")
            # else:
            #     st.caption("⚠️ XLSX not updated (probably open in Excel). CSV is saved.")

            # st.write(f"Score: **{sum_correct_answers()} / {TOTAL_QUESTIONS}**")
            # st.write(f"Total errors: **{sum_wrong_answers()}**")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Restart", key="quiz_restart", width='stretch'):
                    # restart full flow (Practice -> Get Ready -> Main)
                    st.session_state.quiz_started = False
                    st.session_state.quiz_phase = "idle"
                    st.session_state.run_prepared = False
                    st.rerun()

            with c2:
                if st.button("Close", key="quiz_close", width='stretch'):
                    st.session_state.quiz_started = False
                    st.session_state.quiz_phase = "idle"
                    st.session_state.run_prepared = False
                    st.rerun()
            return

        # ------------------------------------------------------------
        # Main Quiz Questions (TIMED)
        # ------------------------------------------------------------
        ensure_question_state_for_current_idx()
        flash_css()

        q = QUESTIONS[st.session_state.quiz_q_idx]
        q_text = q["q"].split("\n\n")
        main = q_text[0]
        focus = q_text[1] if len(q_text) > 1 else ""

        _set_year_override_from_question(main)  # parse ONLY the first line

        st.markdown(
            f"""
            <div class='quiz-q'>
                <b>{main}</b>
                <br><br>
                <div style='text-align:center; font-weight:bold; font-size:18px;'>
                    {focus}
                </div>
                <br>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Debounced buttons: disable immediately after first click
        for i, text in enumerate(q["choices"]):
            clicked = st.button(
                text,
                key=f"quiz_choice_{st.session_state.quiz_q_idx}_{i}",
                width='stretch',
                disabled=st.session_state.quiz_input_locked,
            )

            if clicked:
                # backend debounce (in case UI disable lags)
                if st.session_state.quiz_input_locked:
                    continue

                # lock immediately so rapid extra clicks do nothing
                st.session_state.quiz_input_locked = True

                # autoscroll to top (rendered for 2 consecutive reruns for reliability)
                st.session_state.quiz_scroll_ticks = 2

                # duration measured in Python
                start_ts = st.session_state.get("quiz_q_start_ts")
                elapsed = (time.time() - start_ts) if start_ts else None

                correct_idx = QUESTIONS[st.session_state.quiz_q_idx]["correct"]
                error = 0 if i == correct_idx else 1
                _record_trial(elapsed, error)

                choose(i)
                st.rerun()
