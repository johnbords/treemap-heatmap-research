import time
import math
import streamlit as st
from streamlit_autorefresh import st_autorefresh


def render_quiz():
    """
    Quiz rendered INSIDE the sidebar so it stays visible while scrolling.
    """

    # -------------------------
    # Quiz data
    # -------------------------
    QUESTIONS = [

        # -------------------------
        # Experimental Object 1 (1998–2002)
        # -------------------------
        {
            "q": "Among 1999, 2000, and 2001, which year has the highest average popularity across the genres shown?",
            "choices": ["1999", "2000", "2001"],
            "answer_idx": 0,
        },
        {
            "q": "Compared to 1999 and 2001, how is Genre Y’s popularity in 2000?",
            "choices": [
                "Lower than both years",
                "Higher than both years",
                "In between the two years",
            ],
            "answer_idx": 0,
        },
        {
            "q": "From 2001 to 2002, which genre shows the biggest increase in popularity?",
            "choices": ["Genre X", "Genre Y", "Genre Z"],
            "answer_idx": 0,
        },
        {
            "q": "Between 1998 and 2002, which genre shows the most consistent popularity (least change)?",
            "choices": ["Genre X", "Genre Y", "Genre Z"],
            "answer_idx": 0,
        },

        # -------------------------
        # Experimental Object 2 (2003–2007)
        # -------------------------
        {
            "q": "In 2004, which genre (X or Y) changed more compared to 2003?",
            "choices": ["Genre X", "Genre Y"],
            "answer_idx": 0,
        },
        {
            "q": "Between 2003 and 2007, which year shows the biggest difference between Genre X and Genre Y?",
            "choices": ["2003", "2004", "2005", "2006", "2007"],
            "answer_idx": 0,
        },
        {
            "q": "From 2003 to 2007, does Genre X mostly increase, decrease, or stay stable?",
            "choices": ["Increase", "Decrease", "Stay stable"],
            "answer_idx": 0,
        },

        # -------------------------
        # Experimental Object 3 (2008–2012)
        # -------------------------
        {
            "q": "Between 2008 and 2012, in which year does Genre X show the biggest change compared to the previous year?",
            "choices": ["2009", "2010", "2011"],
            "answer_idx": 0,
        },
        {
            "q": "Looking at Genre X from 2008 to 2012, what happens most of the time?",
            "choices": ["It goes up", "It goes down", "It goes up and down"],
            "answer_idx": 0,
        },
        {
            "q": "From 2011 to 2012, which genre shows the largest change in popularity?",
            "choices": ["Genre X", "Genre Y", "Genre Z"],
            "answer_idx": 0,
        },
        {
            "q": "Which year (2008–2012) has the highest overall popularity across all genres shown?",
            "choices": ["2008", "2009", "2010", "2011", "2012"],
            "answer_idx": 0,
        },
        {
            "q": "Between 2008 and 2012, which genre shows the most fluctuation (up and down changes)?",
            "choices": ["Genre X", "Genre Y", "Genre Z"],
            "answer_idx": 0,
        },
    ]

    # =========================
    # CONFIG (easy to toggle)
    # =========================
    TIME_LIMIT = 10                   # per question seconds
    USE_TRANSITION_COUNTDOWN = False  # True = show 3..2..1, False = show "Loading next question..."
    TRANSITION_SECONDS = 3            # used only if USE_TRANSITION_COUNTDOWN is True
    LOADING_SECONDS = 0.35            # used only if USE_TRANSITION_COUNTDOWN is False (micro transition)
    REFRESH_MS_QUIZ = 100
    REFRESH_MS_TRANSITION = 50

    # -------------------------
    # Namespaced session state
    # -------------------------
    if "quiz_phase" not in st.session_state:
        st.session_state.quiz_phase = "waiting"  # waiting | countdown | quiz | between | done
    if "quiz_countdown_t0" not in st.session_state:
        st.session_state.quiz_countdown_t0 = None
    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = 0
    if "quiz_q_start" not in st.session_state:
        st.session_state.quiz_q_start = None
    if "quiz_locked" not in st.session_state:
        st.session_state.quiz_locked = False
    if "quiz_transition_t0" not in st.session_state:
        st.session_state.quiz_transition_t0 = None

    # -------------------------
    # Helpers
    # -------------------------
    def start_over():
        st.session_state.quiz_phase = "waiting"
        st.session_state.quiz_countdown_t0 = None
        st.session_state.quiz_idx = 0
        st.session_state.quiz_q_start = None
        st.session_state.quiz_locked = False
        st.session_state.quiz_transition_t0 = None

    def start_quiz():
        st.session_state.quiz_phase = "countdown"
        st.session_state.quiz_countdown_t0 = time.time()
        st.session_state.quiz_idx = 0
        st.session_state.quiz_locked = False
        st.session_state.quiz_q_start = None
        st.session_state.quiz_transition_t0 = None

    def start_question_timer():
        st.session_state.quiz_q_start = time.time()

    def begin_transition_to_next():
        """Called when user answers OR time runs out."""
        st.session_state.quiz_locked = True
        st.session_state.quiz_transition_t0 = time.time()
        st.session_state.quiz_phase = "between"

    def advance_question_or_finish():
        st.session_state.quiz_idx += 1
        st.session_state.quiz_locked = False
        st.session_state.quiz_transition_t0 = None

        if st.session_state.quiz_idx >= len(QUESTIONS):
            st.session_state.quiz_phase = "done"
        else:
            st.session_state.quiz_phase = "quiz"
            start_question_timer()

    # -------------------------
    # Sidebar Quiz UI (follows scroll)
    # -------------------------
    with st.sidebar:
        st.divider()
        st.header("Quiz")

        # Start over button (for retake)
        if st.button("🔄 Start over", use_container_width=True, key="quiz_start_over_top"):
            start_over()
            st.rerun()

        # -------------------------
        # Phase 1: Waiting
        # -------------------------
        if st.session_state.quiz_phase == "waiting":
            if st.button("▶️ Start Quiz", use_container_width=True, key="quiz_start_btn"):
                start_quiz()
                st.rerun()
            return

        # -------------------------
        # Phase 2: 3-second countdown (start)
        # -------------------------
        if st.session_state.quiz_phase == "countdown":
            st_autorefresh(interval=REFRESH_MS_TRANSITION, key="quiz_prestart_tick")

            elapsed = time.time() - st.session_state.quiz_countdown_t0
            rem_f = max(3.0 - elapsed, 0.0)
            rem_int = math.ceil(rem_f)

            st.markdown(
                f"""
                <div style='text-align: center; padding-top: 8px;'>
                    <h3 style='margin-bottom: 10px;'>Get Ready!</h3>
                    <div style='font-size: 72px; font-weight: 800; line-height: 1;'>{rem_int}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if rem_f <= 0:
                st.session_state.quiz_phase = "quiz"
                start_question_timer()
                st.rerun()
            return

        # -------------------------
        # Phase 3.5: Between questions
        # -------------------------
        if st.session_state.quiz_phase == "between":
            st_autorefresh(interval=REFRESH_MS_TRANSITION, key="quiz_between_tick")

            t0 = st.session_state.quiz_transition_t0 or time.time()
            elapsed = time.time() - t0

            if USE_TRANSITION_COUNTDOWN:
                rem_f = max(float(TRANSITION_SECONDS) - elapsed, 0.0)
                rem_int = math.ceil(rem_f)

                st.markdown(
                    f"""
                    <div style='text-align: center; padding-top: 8px;'>
                        <h3 style='margin-bottom: 10px;'>Next question in</h3>
                        <div style='font-size: 72px; font-weight: 800; line-height: 1;'>{rem_int}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if rem_f <= 0:
                    advance_question_or_finish()
                    st.rerun()
            else:
                st.markdown(
                    """
                    <div style='text-align: center; padding-top: 10px;'>
                        <h3>Loading next question...</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if elapsed >= LOADING_SECONDS:
                    advance_question_or_finish()
                    st.rerun()
            return

        # -------------------------
        # Phase 3: Quiz question
        # -------------------------
        if st.session_state.quiz_phase == "quiz":
            st_autorefresh(interval=REFRESH_MS_QUIZ, key="quiz_tick")

            q = QUESTIONS[st.session_state.quiz_idx]

            elapsed = time.time() - st.session_state.quiz_q_start
            rem_f = max(TIME_LIMIT - elapsed, 0.0)
            rem_int = math.ceil(rem_f)

            st.markdown(f"### Q{st.session_state.quiz_idx + 1}")
            st.write(q["q"])
            st.markdown(f"**⏱️ {rem_int}s**")
            st.progress(rem_f / TIME_LIMIT)

            # Timeout -> transition (no correct answer reveal)
            if rem_f <= 0 and not st.session_state.quiz_locked:
                begin_transition_to_next()
                st.rerun()
                return

            cols = st.columns(2)
            clicked = None
            for i, choice in enumerate(q["choices"]):
                with cols[i % 2]:
                    if st.button(
                        choice,
                        use_container_width=True,
                        disabled=st.session_state.quiz_locked,
                        key=f"quiz_ans_{st.session_state.quiz_idx}_{i}",
                    ):
                        clicked = i

            # Click -> transition (no feedback)
            if clicked is not None and not st.session_state.quiz_locked:
                begin_transition_to_next()
                st.rerun()
            return

        # -------------------------
        # Done
        # -------------------------
        if st.session_state.quiz_phase == "done":
            st.success("Finished! 🎉")
            if st.button("🔄 Start over", use_container_width=True, key="quiz_start_over_done"):
                start_over()
                st.rerun()
            return