import streamlit as st

# ---------------------------
# Config
# ---------------------------
QUIZ_COLOR = "#2e7dff"
FADE_SECONDS = 1.2

TOTAL_QUESTIONS = 10

QUESTIONS = [
    {"q": "1) What does CPU stand for?",
     "choices": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Compute Power Unit"],
     "correct": 0},
    {"q": "2) Which data structure is FIFO?",
     "choices": ["Stack", "Queue", "Tree", "Graph"],
     "correct": 1},
    {"q": "3) In Python, what does `len(x)` return?",
     "choices": ["Last element", "Type of x", "Number of items", "Memory address"],
     "correct": 2},
    {"q": "4) Which one is NOT an OOP concept?",
     "choices": ["Encapsulation", "Inheritance", "Compilation", "Polymorphism"],
     "correct": 2},
    {"q": "5) What is the time complexity of binary search?",
     "choices": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
     "correct": 1},
    {"q": "6) Which protocol is used for secure browsing?",
     "choices": ["HTTP", "FTP", "HTTPS", "SMTP"],
     "correct": 2},
    {"q": "7) What does RAM stand for?",
     "choices": ["Random Access Memory", "Read Access Memory", "Run All Memory", "Random Allocation Module"],
     "correct": 0},
    {"q": "8) Which is a relational database?",
     "choices": ["MongoDB", "Redis", "PostgreSQL", "Neo4j"],
     "correct": 2},
    {"q": "9) Python single-line comment symbol?",
     "choices": ["//", "#", "--", "/* */"],
     "correct": 1},
    {"q": "10) What does IP stand for?",
     "choices": ["Internet Protocol", "Internal Process", "Interface Port", "Internet Path"],
     "correct": 0},
]


def compute_score():
    return sum(
        1 for i, ans in enumerate(st.session_state.quiz_answers)
        if QUESTIONS[i]["correct"] == ans
    )


def reset_quiz():
    st.session_state.quiz_q_idx = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_flash_id += 1


def start_quiz():
    st.session_state.quiz_started = True
    reset_quiz()
    st.rerun()


def choose(choice_idx: int):
    st.session_state.quiz_answers.append(choice_idx)
    st.session_state.quiz_q_idx += 1
    st.session_state.quiz_flash_id += 1

def flash_css():
    if st.session_state.quiz_flash_id <= 0:
        return

    anim = f"quizFade_{st.session_state.quiz_flash_id}"

    st.markdown(
        f"""
        <style>
        @keyframes {anim} {{
          0%   {{ color: {QUIZ_COLOR}; }}
          100% {{ color: #000000; }}
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


def render_quiz():

    # ---------------------------
    # State
    # ---------------------------
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    if "quiz_q_idx" not in st.session_state:
        st.session_state.quiz_q_idx = 0

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = []

    if "quiz_flash_id" not in st.session_state:
        st.session_state.quiz_flash_id = 0

    # ---------------------------
    # Sidebar Render
    # ---------------------------
    with st.sidebar:
        st.header("Quiz")

        # Start screen
        if not st.session_state.quiz_started:
            st.info("Click **Start** to begin.")
            if st.button("Start", key="quiz_start", use_container_width=True):
                start_quiz()
            return

        flash_css()

        # Finished screen
        if st.session_state.quiz_q_idx >= TOTAL_QUESTIONS:
            st.success("Quiz finished!")
            st.write(f"Score: **{compute_score()} / {TOTAL_QUESTIONS}**")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Restart", key="quiz_restart", use_container_width=True):
                    reset_quiz()
                    st.rerun()
            with c2:
                if st.button("End", key="quiz_end", use_container_width=True):
                    st.session_state.quiz_started = False
                    st.rerun()

            return

        # Question screen
        q = QUESTIONS[st.session_state.quiz_q_idx]
        st.markdown(f"<div class='quiz-q'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        st.caption(f"Question {st.session_state.quiz_q_idx + 1} / {TOTAL_QUESTIONS}")

        for i, text in enumerate(q["choices"]):
            if st.button(text, key=f"quiz_choice_{st.session_state.quiz_q_idx}_{i}", use_container_width=True):
                choose(i)
                st.rerun()