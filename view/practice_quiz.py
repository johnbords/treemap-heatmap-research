# view/practice_quiz.py

import streamlit as st

PRACTICE_QUESTIONS = [
    {"q": "1) In which year, between 2001 and 2004, was Rock more popular than Country?",
     "choices": ["2001", "2002", "2003", "2004"],
     "correct": 1},

    {"q": "2) In the year 2003, among Rock, Dance/Electronic, Latin, and Country, which genre has the highest popularity?",
     "choices": ["Rock", "Dance/Electronic", "Latin", "Country"],
     "correct": 2},

    {"q": "3) In 1998 to 2020, blues' popularity mostly...",
     "choices": ["Goes up", "Goes down", "None of the above"],
     "correct": 2},
]

TOTAL = len(PRACTICE_QUESTIONS)


def render_practice_quiz():
    # ✅ If main quiz is active, do NOT render the practice button/UI
    if st.session_state.get("active_quiz") == "main":
        return

    # ✅ Optional: also hide while the main quiz has started (extra safety)
    if st.session_state.get("quiz_started") is True:
        return
    # ---------------------------
    # State init
    # ---------------------------
    st.session_state.setdefault("practice_mode", False)
    st.session_state.setdefault("practice_q_idx", 0)
    st.session_state.setdefault("practice_answers", [])
    st.session_state.setdefault("active_quiz", None)

    with st.sidebar:

        # ---------------------------
        # Entry Button (always visible)
        # ---------------------------
        if not st.session_state.practice_mode:
            if st.button("Practice questions", use_container_width=True):
                st.session_state.practice_mode = True
                st.session_state.active_quiz = "practice"  # ✅ ADD THIS
                st.session_state.quiz_started = False
                st.session_state.practice_q_idx = 0
                st.session_state.practice_answers = []
                st.rerun()
            return

        # ---------------------------
        # Practice Quiz UI
        # ---------------------------
        st.header("Practice Questions")

        # Finished
        if st.session_state.practice_q_idx >= TOTAL:
            score = sum(
                1 for i, ans in enumerate(st.session_state.practice_answers)
                if PRACTICE_QUESTIONS[i]["correct"] == ans
            )

            st.success("Practice finished!")
            st.write(f"Score: **{score} / {TOTAL}**")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Restart", use_container_width=True):
                    st.session_state.practice_q_idx = 0
                    st.session_state.practice_answers = []
                    st.rerun()

            with col2:
                if st.button("Close", use_container_width=True):
                    st.session_state.practice_mode = False
                    st.session_state.active_quiz = None  # ✅ ADD THIS
                    st.rerun()

            return

        # Question
        q_idx = st.session_state.practice_q_idx
        q = PRACTICE_QUESTIONS[q_idx]

        st.markdown(f"**{q['q']}**")
        st.caption(f"Question {q_idx + 1} / {TOTAL}")

        for i, text in enumerate(q["choices"]):
            if st.button(text, key=f"practice_choice_{q_idx}_{i}", use_container_width=True):
                st.session_state.practice_answers.append(i)
                st.session_state.practice_q_idx += 1
                st.rerun()