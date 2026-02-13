# demo_app.py

import streamlit as st
import uuid
from js_timer_component import countdown

st.title("JS Countdown → Python Flag (Streamlit Components v2)")

secs = st.slider("Seconds", 3, 30, 10)

mode = st.radio("Interrupt Mode", ["stop", "reset"])

if "timer_key" not in st.session_state:
    st.session_state.timer_key = str(uuid.uuid4())
if "run_id" not in st.session_state:
    st.session_state.run_id = None
if "done_payload" not in st.session_state:
    st.session_state.done_payload = None
if "interrupt_id" not in st.session_state:
    st.session_state.interrupt_id = ""

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start / Restart"):
        st.session_state.timer_key = str(uuid.uuid4())
        st.session_state.run_id = str(uuid.uuid4())
        st.session_state.done_payload = None
        st.session_state.interrupt_id = ""  # clear any previous interrupt

with col2:
    if st.button("Interrupt"):
        # Changing this value signals JS to interrupt and report remaining time.
        st.session_state.interrupt_id = str(uuid.uuid4())

with col3:
    if st.button("Clear"):
        st.session_state.timer_key = str(uuid.uuid4())
        st.session_state.run_id = None
        st.session_state.done_payload = None
        st.session_state.interrupt_id = ""

result, run_id = countdown(
    secs,
    key=st.session_state.timer_key,
    run_id=st.session_state.run_id,
    interrupt_id=st.session_state.interrupt_id,
    interrupt_mode=mode,
)
st.session_state.run_id = run_id

if getattr(result, "done", None) is not None:
    st.session_state.done_payload = result.done

payload = st.session_state.done_payload

if payload:
    if payload.get("interrupted"):
        st.warning(
            f"⏸️ INTERRUPTED — remaining: {payload.get('remaining','00:00')} | "
            f"elapsed: {payload.get('elapsed','00:00')}"
        )
    elif payload.get("finished"):
        st.success(
            f"✅ DONE — elapsed: {payload.get('elapsed','00:00')} | "
            f"remaining: {payload.get('remaining','00:00')}"
        )