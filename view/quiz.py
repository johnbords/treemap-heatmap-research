import os
import uuid
import csv
from typing import List, Optional

import streamlit as st

from view import js_timer_component  # your existing JS timer component


# ---------------------------
# Config
# ---------------------------
QUIZ_COLOR = "#6FA8DC"
FADE_SECONDS = 0.5

QUESTION_SECONDS = 15
NO_ANSWER = -1  # stored when timer expires

RESULTS_DIR = "results"


# ---------------------------
# Questions (hardcoded for now)
# ---------------------------
QUESTIONS = [
    {"q": "1) In which years is Pop higher than Hip Hop?",
     "choices": ["1998 and 1999", "2000 and 2002", "2001 and 2002", "Only 2000"],
     "correct": 1},

    {"q": "2) In 2000, which genre is second highest?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 0},

    {"q": "3) In 2002, which genre is the lowest?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 2},

    {"q": "4) From 1999 to 2002, which genre is highest in most years?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 3},

    {"q": "5) In 2007, which genre is second highest?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 1},

    {"q": "6) From 2003 to 2007, Hip Hop mostly:",
     "choices": ["Goes up", "Goes down", "Goes up and down", "Stays about the same"],
     "correct": 1},

    {"q": "7) In which year is Latin most popular?",
     "choices": ["2003", "2004", "2006", "2007"],
     "correct": 2},

    {"q": "8) In 2005, which genre is in the middle (not highest and not lowest)?",
     "choices": ["Pop", "Hip Hop", "R&B"],
     "correct": 0},

    {"q": "9) Between 2008 and 2012, in which year is Metal the highest?",
     "choices": ["2008", "2009", "2010", "2011", "2012"],
     "correct": 1},

    {"q": "10) In 2010, which genre is the highest?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 1},
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

    # Save to temp then replace (atomic-ish)
    wb.save(tmp_path)
    wb.close()

    # Replace the final xlsx
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
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        if ans != NO_ANSWER and QUESTIONS[i]["correct"] == ans
    )


def sum_wrong_answers() -> int:
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        if ans == NO_ANSWER or QUESTIONS[i]["correct"] != ans
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

    # timer state
    st.session_state.quiz_pending_choice = None
    st.session_state.quiz_q_timer_interrupt_id = ""
    st.session_state.quiz_q_timer_for_idx = None
    st.session_state.quiz_q_timer_key = f"quiz_q_timer_{uuid.uuid4()}"
    st.session_state.quiz_q_timer_run_id = str(uuid.uuid4())

    # critical: process timer_done only once per run_id
    st.session_state.quiz_handled_done_run_id = None


def start_get_ready():
    # lock the output CSV for THIS run based on selected datamap at Start time
    csv_path = _results_csv_path()
    st.session_state.results_csv_path = csv_path

    ensure_csv_file(csv_path, TOTAL_QUESTIONS)
    st.session_state.participant_id = get_next_participant_id(csv_path)

    st.session_state.quiz_started = True
    st.session_state.quiz_phase = "get_ready"
    reset_quiz()

    st.session_state.quiz_ready_key = f"quiz_ready_timer_{uuid.uuid4()}"
    st.session_state.quiz_ready_run_id = str(uuid.uuid4())
    st.rerun()


def choose(choice_idx: int):
    st.session_state.quiz_answers.append(choice_idx)
    st.session_state.quiz_q_idx += 1
    st.session_state.quiz_flash_id += 1

    # hard reset interrupt state when moving forward
    st.session_state.quiz_q_timer_interrupt_id = ""
    st.session_state.quiz_pending_choice = None


def ensure_question_timer_for_current_idx():
    cur = st.session_state.quiz_q_idx
    if st.session_state.quiz_q_timer_for_idx != cur:
        st.session_state.quiz_q_timer_for_idx = cur
        st.session_state.quiz_q_timer_key = f"quiz_q_timer_{uuid.uuid4()}"
        st.session_state.quiz_q_timer_run_id = str(uuid.uuid4())

        st.session_state.quiz_q_timer_interrupt_id = ""
        st.session_state.quiz_pending_choice = None

        # reset "handled done" guard for this new run_id
        st.session_state.quiz_handled_done_run_id = None


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
    try:
        xlsx_path = convert_csv_to_xlsx(csv_path)
        st.session_state.converted_to_xlsx = True
        st.session_state.results_xlsx_path = xlsx_path
    except PermissionError:
        # XLSX is likely open in Excel
        st.session_state.converted_to_xlsx = False
        st.session_state.results_xlsx_path = _results_xlsx_path_from_csv(csv_path)
        st.warning(
            "Saved to CSV, but could not update the XLSX because it is likely open in Excel.\n"
            "Close the XLSX file, then the next participant will update it."
        )


# ============================================================
# Main render
# ============================================================
def render_quiz():
    # ---------------------------
    # State init
    # ---------------------------
    st.session_state.setdefault("quiz_started", False)
    st.session_state.setdefault("quiz_phase", "idle")  # idle|get_ready|quiz
    st.session_state.setdefault("quiz_q_idx", 0)
    st.session_state.setdefault("quiz_answers", [])
    st.session_state.setdefault("quiz_flash_id", 0)

    st.session_state.setdefault("quiz_ready_key", f"quiz_ready_timer_{uuid.uuid4()}")
    st.session_state.setdefault("quiz_ready_run_id", str(uuid.uuid4()))

    st.session_state.setdefault("participant_id", None)
    st.session_state.setdefault("trial_times", [])
    st.session_state.setdefault("trial_errors", [])
    st.session_state.setdefault("saved_to_disk", False)
    st.session_state.setdefault("converted_to_xlsx", False)

    st.session_state.setdefault("quiz_pending_choice", None)
    st.session_state.setdefault("quiz_q_timer_interrupt_id", "")
    st.session_state.setdefault("quiz_q_timer_for_idx", None)
    st.session_state.setdefault("quiz_q_timer_key", f"quiz_q_timer_{uuid.uuid4()}")
    st.session_state.setdefault("quiz_q_timer_run_id", str(uuid.uuid4()))
    st.session_state.setdefault("quiz_handled_done_run_id", None)

    st.session_state.setdefault("results_csv_path", None)
    st.session_state.setdefault("results_xlsx_path", None)

    with st.sidebar:
        st.header("Quiz")

        # Idle
        if not st.session_state.quiz_started or st.session_state.quiz_phase == "idle":
            st.info("Click **Start** to begin.")
            if st.button("Start", key="quiz_start", use_container_width=True):
                start_get_ready()
            return

        # Get Ready
        if st.session_state.quiz_phase == "get_ready":
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

        # Finished (AUTO SAVE + AUTO CONVERT AFTER 1 PARTICIPANT)
        if st.session_state.quiz_q_idx >= TOTAL_QUESTIONS:
            _save_and_convert_if_needed()

            flash_css()
            st.success("Quiz finished!")

            chart = st.session_state.get("chart_type_radio", "Heatmap")
            st.write(f"Participant ID: **{st.session_state.participant_id}**")
            st.write(f"Datamap: **{chart}**")
            st.write(f"CSV: `{st.session_state.get('results_csv_path') or _results_csv_path()}`")

            xlsx_path = st.session_state.get("results_xlsx_path") or _results_xlsx_path_from_csv(
                st.session_state.get("results_csv_path") or _results_csv_path()
            )
            st.write(f"XLSX: `{xlsx_path}`")

            if st.session_state.converted_to_xlsx:
                st.caption("✅ XLSX updated after this participant.")
            else:
                st.caption("⚠️ XLSX not updated (probably open in Excel). CSV is saved.")

            st.write(f"Score: **{sum_correct_answers()} / {TOTAL_QUESTIONS}**")
            st.write(f"Total errors: **{sum_wrong_answers()}**")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Restart", key="quiz_restart", use_container_width=True):
                    start_get_ready()
            with c2:
                if st.button("Close", key="quiz_close", use_container_width=True):
                    st.session_state.quiz_started = False
                    st.session_state.quiz_phase = "idle"
                    st.rerun()
            return

        # Question timer
        ensure_question_timer_for_current_idx()

        q_timer_style = dict(js_timer_component.TIMER_STYLE)
        q_timer_style["show_bar"] = True
        q_timer_style["seconds_only"] = True
        q_timer_style["align"] = "left"

        timer_result, _ = js_timer_component.countdown(
            QUESTION_SECONDS,
            key=st.session_state.quiz_q_timer_key,
            run_id=st.session_state.quiz_q_timer_run_id,
            interrupt_id=st.session_state.quiz_q_timer_interrupt_id,
            interrupt_mode="stop",
            style=q_timer_style,
        )

        timer_done = (timer_result or {}).get("done")

        # Fix #1: ignore stale events
        if timer_done and timer_done.get("run_id") != st.session_state.quiz_q_timer_run_id:
            timer_done = None

        # Fix #2: process done only once per run_id
        if timer_done and st.session_state.quiz_handled_done_run_id == st.session_state.quiz_q_timer_run_id:
            timer_done = None

        # Interrupted (answer click)
        if (
            timer_done
            and timer_done.get("interrupted") is True
            and st.session_state.quiz_pending_choice is not None
        ):
            st.session_state.quiz_handled_done_run_id = st.session_state.quiz_q_timer_run_id

            choice_idx = st.session_state.quiz_pending_choice
            elapsed = timer_done.get("elapsed")

            correct_idx = QUESTIONS[st.session_state.quiz_q_idx]["correct"]
            error = 0 if choice_idx == correct_idx else 1
            _record_trial(elapsed, error)

            st.session_state.quiz_pending_choice = None
            st.session_state.quiz_q_timer_interrupt_id = ""

            choose(choice_idx)
            st.rerun()

        # Timeout
        if timer_done and timer_done.get("finished") is True:
            st.session_state.quiz_handled_done_run_id = st.session_state.quiz_q_timer_run_id

            elapsed = timer_done.get("elapsed")
            _record_trial(elapsed, 1)

            st.session_state.quiz_answers.append(NO_ANSWER)
            st.session_state.quiz_q_idx += 1
            st.session_state.quiz_flash_id += 1
            st.rerun()

        # Question + choices
        flash_css()

        q = QUESTIONS[st.session_state.quiz_q_idx]
        st.markdown(f"<div class='quiz-q'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        st.caption(f"Question {st.session_state.quiz_q_idx + 1} / {TOTAL_QUESTIONS}")

        for i, text in enumerate(q["choices"]):
            if st.button(
                text,
                key=f"quiz_choice_{st.session_state.quiz_q_idx}_{i}",
                use_container_width=True,
            ):
                # interrupt timer so we capture elapsed reliably
                st.session_state.quiz_pending_choice = i
                st.session_state.quiz_q_timer_interrupt_id = str(uuid.uuid4())
                st.rerun()