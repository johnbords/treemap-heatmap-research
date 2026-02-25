import streamlit as st
import uuid

from view import js_timer_component  # integrates your JS timer component

# ---------------------------
# Config
# ---------------------------
QUIZ_COLOR = "#6FA8DC"
FADE_SECONDS = 0.5
TOTAL_QUESTIONS = 10
QUESTION_SECONDS = 25
NO_ANSWER = -1  # stored when timer expires

QUESTIONS = [

    # =============================
    # Experimental Object 1 (1998–2002)
    # =============================

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


    # =============================
    # Experimental Object 2 (2003–2007)
    # =============================

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


    # =============================
    # Experimental Object 3 (2008–2012)
    # =============================

    {"q": "9) Between 2008 and 2012, in which year is Metal the highest?",
     "choices": ["2008", "2009", "2010", "2011", "2012"],
     "correct": 1},

    {"q": "10) In 2010, which genre is the highest?",
     "choices": ["Pop", "Hip Hop", "R&B", "Metal"],
     "correct": 1},

    {"q": "11) Between 2011 and 2012, which genre reaches the highest popularity?",
     "choices": ["Pop", "Hip Hop", "R&B", "Folk/Acoustic"],
     "correct": 3},

    {"q": "12) In 2011, which genre is the lowest?",
     "choices": ["Pop", "Hip Hop", "R&B"],
     "correct": 2},
]


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

        /* Question */
        [data-testid="stSidebar"] .quiz-q,
        [data-testid="stSidebar"] .quiz-q * {{
          animation: {anim} {FADE_SECONDS}s ease-out 0s 1;
        }}

        /* All quiz choice buttons in sidebar */
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
        # Ignore NO_ANSWER entries in scoring
        # if ans != NO_ANSWER and QUESTIONS[i]["correct"] == ans
        if QUESTIONS[i]["correct"] == ans
    )

def sum_wrong_answers() -> int:
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        # Ignore NO_ANSWER entries in scoring
        # if ans != NO_ANSWER and QUESTIONS[i]["correct"] == ans
        if ans == NO_ANSWER or QUESTIONS[i]["correct"] != ans
    )

def reset_quiz():
    st.session_state.quiz_q_idx = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_flash_id += 1


def start_get_ready():
    # Start → Get Ready phase (3-second countdown)
    st.session_state.quiz_started = True
    st.session_state.quiz_phase = "get_ready"
    reset_quiz()

    # Force-remount the timer each time Start is clicked
    st.session_state.quiz_ready_key = f"quiz_ready_timer_{uuid.uuid4()}"
    st.session_state.quiz_ready_run_id = str(uuid.uuid4())

    st.rerun()


def choose(choice_idx: int):
    st.session_state.quiz_answers.append(choice_idx)
    st.session_state.quiz_q_idx += 1
    st.session_state.quiz_flash_id += 1


def ensure_question_timer_for_current_idx():
    """
    Remount the 15s timer every time we enter a new question index.
    """
    if "quiz_q_timer_for_idx" not in st.session_state:
        st.session_state.quiz_q_timer_for_idx = None
    if "quiz_q_timer_key" not in st.session_state:
        st.session_state.quiz_q_timer_key = f"quiz_q_timer_{uuid.uuid4()}"
    if "quiz_q_timer_run_id" not in st.session_state:
        st.session_state.quiz_q_timer_run_id = str(uuid.uuid4())

    cur = st.session_state.quiz_q_idx
    if st.session_state.quiz_q_timer_for_idx != cur:
        st.session_state.quiz_q_timer_for_idx = cur
        st.session_state.quiz_q_timer_key = f"quiz_q_timer_{uuid.uuid4()}"
        st.session_state.quiz_q_timer_run_id = str(uuid.uuid4())


def render_quiz():
    # ---------------------------
    # State
    # ---------------------------
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    if "quiz_phase" not in st.session_state:
        # phases: "idle" | "get_ready" | "quiz"
        st.session_state.quiz_phase = "idle"

    if "quiz_q_idx" not in st.session_state:
        st.session_state.quiz_q_idx = 0

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = []

    if "quiz_flash_id" not in st.session_state:
        st.session_state.quiz_flash_id = 0

    if "quiz_ready_key" not in st.session_state:
        st.session_state.quiz_ready_key = f"quiz_ready_timer_{uuid.uuid4()}"

    if "quiz_ready_run_id" not in st.session_state:
        st.session_state.quiz_ready_run_id = str(uuid.uuid4())

    # ---------------------------
    # Sidebar Render
    # ---------------------------
    with st.sidebar:
        st.header("Quiz")

        # Start screen
        if not st.session_state.quiz_started or st.session_state.quiz_phase == "idle":
            st.info("Click **Start** to begin.")
            if st.button("Start", key="quiz_start", use_container_width=True):
                start_get_ready()
            return

        # ---------------------------
        # Get Ready phase (3s countdown)
        # ---------------------------
        if st.session_state.quiz_phase == "get_ready":
            st.markdown(
                "<h1 style='font-size:30px; text-align:center;'>Get Ready</h1>",
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

        # ---------------------------
        # Finished screen (NO TIMER HERE)
        # ---------------------------
        if st.session_state.quiz_q_idx >= TOTAL_QUESTIONS:
            flash_css()

            st.success("Quiz finished!")
            st.write(f"Score: **{sum_correct_answers()} / {TOTAL_QUESTIONS}**")
            st.write(f"Wrong answers total **{sum_wrong_answers()}**")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Restart", key="quiz_restart", use_container_width=True):
                    start_get_ready()
            with c2:
                if st.button("End", key="quiz_end", use_container_width=True):
                    st.session_state.quiz_started = False
                    st.session_state.quiz_phase = "idle"
                    st.rerun()
            return

        # ---------------------------
        # Question timer (WITH BAR) — placed between header and question
        # ---------------------------
        ensure_question_timer_for_current_idx()

        q_timer_style = dict(js_timer_component.TIMER_STYLE)
        q_timer_style["show_bar"] = True
        q_timer_style["seconds_only"] = True
        q_timer_style["align"] = "left"
        # (optional) adjust size if you want:
        # q_timer_style["font_size"] = "28px"

        timer_result, _ = js_timer_component.countdown(
            QUESTION_SECONDS,
            key=st.session_state.quiz_q_timer_key,
            run_id=st.session_state.quiz_q_timer_run_id,
            style=q_timer_style,
        )

        timer_done = (timer_result or {}).get("done")
        if timer_done and timer_done.get("finished") is True:
            # time's up → record NO_ANSWER and advance
            st.session_state.quiz_answers.append(NO_ANSWER)
            st.session_state.quiz_q_idx += 1
            st.session_state.quiz_flash_id += 1
            st.rerun()

        # ---------------------------
        # Normal quiz flow
        # ---------------------------
        flash_css()

        q = QUESTIONS[st.session_state.quiz_q_idx]
        st.markdown(f"<div class='quiz-q'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        st.caption(f"Question {st.session_state.quiz_q_idx + 1} / {TOTAL_QUESTIONS}")

        for i, text in enumerate(q["choices"]):
            if st.button(text, key=f"quiz_choice_{st.session_state.quiz_q_idx}_{i}", use_container_width=True):
                choose(i)
                st.rerun()