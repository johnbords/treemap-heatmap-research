import streamlit as st
import uuid

# -----------------------------
# V2 component (JS-only, inline)
# -----------------------------

# Global styling knobs (edit these in Python only)
TIMER_STYLE = {
    "font_size": "40px",          # e.g. "2rem", "48px"
    "font_color": "#ffffff",      # any CSS color
    "align": "left",              # "left", "center", "right"
    "seconds_only": False,         # True = show only seconds

    # Progress bar settings
    "bar_color": "#ff4b4b",       # fill color
    "track_color": "#0e1117",  # background/track color
    "reverse_bar": True,         # True = bar shrinks instead of grows
    "show_bar": True,             # False = hide bar completely
    "precision": 3,  # number of decimal places for elapsed/remaining

    # Positioning (optional)
    "position": "static",         # "static" (default) or "fixed"
    "top": "12px",                # used if position == "fixed"
    "right": "12px",              # used if position == "fixed"
    "bottom": "auto",             # used if position == "fixed"
    "left": "auto",               # used if position == "fixed"
    "z_index": 1000,              # used if position == "fixed"
}

HTML = """
<div class="wrap">
  <!-- <div class="label">Time left</div> -->
  <div id="time" class="time">--:--</div>
  <div class="bar">
    <div id="fill" class="fill"></div>
  </div>
</div>
"""

CSS = """
.wrap {
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  text-align: var(--align);

  /* positioning (optional) */
  position: var(--pos);
  top: var(--top);
  right: var(--right);
  bottom: var(--bottom);
  left: var(--left);
  z-index: var(--z);
}

.label {
  font-size: 0.9rem;
  opacity: 0.75;
  margin-bottom: 6px;
}

.time {
  font-size: var(--font-size);
  font-weight: 700;
  line-height: 1;
  margin-bottom: 10px;
  color: var(--font-color);
}

.bar {
  width: 100%;
  height: 10px;
  background: var(--track-color);
  border-radius: 999px;
  overflow: hidden;
  display: var(--bar-display);
}

.fill {
  height: 100%;
  width: 0%;
  background: var(--bar-color);
  transition: width 0.05s linear;
}
"""

JS = r"""
export default function(component) {
  const { data, parentElement, setTriggerValue } = component; // ✅ destructure first
    
    const style = data?.style || {};
    const precision = Number(style.precision ?? 3); // default 3 decimals
    
  const secondsTotal = Math.max(0, Number(data?.seconds ?? 0));
  const runId = String(data?.run_id ?? "no-run-id");
  const interruptId = String(data?.interrupt_id ?? "");
  const interruptMode = String(data?.interrupt_mode ?? "stop"); // ✅ safe now

  const globalStore = (window.__stTimers = window.__stTimers || {});
  const store = (globalStore[runId] = globalStore[runId] || {});
    
    store.rafId = store.rafId ?? null;
    
  const hostEl = (parentElement && parentElement.host) ? parentElement.host : parentElement;

  if (hostEl && hostEl.style) {
    hostEl.style.setProperty("--font-size", style.font_size || "2rem");
    hostEl.style.setProperty("--font-color", style.font_color || "#ffffff");
    hostEl.style.setProperty("--align", style.align || "center");

    hostEl.style.setProperty("--pos", style.position || "static");
    hostEl.style.setProperty("--top", style.top || "auto");
    hostEl.style.setProperty("--right", style.right || "auto");
    hostEl.style.setProperty("--bottom", style.bottom || "auto");
    hostEl.style.setProperty("--left", style.left || "auto");
    hostEl.style.setProperty("--z", String(style.z_index ?? 1000));

    hostEl.style.setProperty("--bar-color", style.bar_color || "#ff4b4b");
    hostEl.style.setProperty("--track-color", style.track_color || "rgba(128,128,128,0.25)");
    hostEl.style.setProperty("--bar-display", style.show_bar === false ? "none" : "block");
  }

  const secondsOnly = Boolean(style.seconds_only);
  const reverseBar = Boolean(style.reverse_bar);

    const root = parentElement?.shadowRoot || parentElement;
    const timeEl = root?.querySelector ? root.querySelector("#time") : null;
    const fillEl = root?.querySelector ? root.querySelector("#fill") : null;

  // Initialize timer state if needed
  if (!store.endAt || store.secondsTotal !== secondsTotal) {
    const t0 = performance.now();
    store.secondsTotal = secondsTotal;
    store.endAt = t0 + secondsTotal * 1000;
    store.doneSent = false;
    store.finished = false;
    store.interrupted = false;
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function fmt(msLeft) {
    const ms = Math.max(0, msLeft);
    const sWhole = Math.floor(ms / 1000);
    const cs = Math.floor((ms % 1000) / 10); // 00..99 (centiseconds)
    if (secondsOnly) return String(Math.ceil(ms / 1000));
    return pad2(sWhole) + ":" + pad2(cs);
  }

  function sendPayload(now, finished, interrupted) {
      const endAtNow = store.endAt;
      const msLeft = Math.max(0, endAtNow - now);
      const totalMs = secondsTotal * 1000;
      const elapsedMs = Math.max(0, totalMs - msLeft);
    
      const factor = Math.pow(10, precision);
    
      const remainingSec = Math.round((msLeft / 1000) * factor) / factor;
      const elapsedSec = Math.round((elapsedMs / 1000) * factor) / factor;
    
      setTriggerValue("done", {
        run_id: runId,
        finished,
        interrupted,
        mode: interrupted ? interruptMode : undefined,
    
        remaining: remainingSec,
        elapsed: elapsedSec,
    
        ms_left: Math.floor(msLeft),
        ms_elapsed: Math.floor(elapsedMs),
      });
    }

  function interrupt(now) {
      if (store.finished || store.interrupted) return;
    
      // Always return snapshot at interruption moment
      sendPayload(now, false, true);
    
        if (interruptMode === "stop") {
          store.doneSent = true;
          store.interrupted = true;
          store.finished = true;
        
            if (store.rafId) cancelAnimationFrame(store.rafId);
            store.rafId = null;
          return;
        }
    
      if (interruptMode === "reset") {
        const t0 = performance.now();
        store.endAt = t0 + secondsTotal * 1000;
        store.doneSent = false;
        store.finished = false;
        store.interrupted = false;
        
        if (store.rafId) cancelAnimationFrame(store.rafId);
        store.rafId = requestAnimationFrame(tick);
        return;
      }
    }

  function tick(now) {
    if (store.finished) return;
    const endAtNow = store.endAt; // ✅ dynamic endAt
    const msLeft = endAtNow - now;

    // Interrupt signal from Python: if interrupt_id changes, interrupt once.
    if (interruptId && store.lastInterruptId !== interruptId) {
      store.lastInterruptId = interruptId;
      interrupt(now);
      return;
    }

    const totalMs = secondsTotal * 1000;
    const elapsed = totalMs - msLeft;
    const progress = secondsTotal === 0 ? 100 : Math.min(100, Math.max(0, (elapsed / totalMs) * 100));

    if (timeEl) timeEl.textContent = fmt(msLeft);

    if (fillEl) {
      fillEl.style.width = reverseBar ? `${100 - progress}%` : `${progress}%`;
    }

    if (msLeft <= 0 && !store.doneSent) {
      store.doneSent = true;
      store.finished = true;

      // Natural completion: return elapsed too
      sendPayload(now, true, false);
      return;
    }

    store.rafId = requestAnimationFrame(tick);
  }

  store.rafId = requestAnimationFrame(tick);

  return () => {
    if (store.rafId) cancelAnimationFrame(store.rafId);
    store.rafId = null;
  };
}
"""

# Register ONCE (important: don’t re-register per-call)
_js_timer = st.components.v2.component(
    "js_countdown_timer",
    html=HTML,
    css=CSS,
    js=JS,
)

def countdown(
    seconds: int,
    *,
    key: str,
    run_id: str | None = None,
    interrupt_id: str | None = None,
    interrupt_mode: str = "stop",  # NEW
    style: dict | None = None,
):
    """
    JS-only countdown.
    - key: MUST change to restart timer (remount)
    - run_id: included in done payload
    - style: optional override; defaults to TIMER_STYLE
    """
    if run_id is None:
        run_id = str(uuid.uuid4())
    if style is None:
        style = TIMER_STYLE

    result = _js_timer(
        data={
            "seconds": int(seconds),
            "run_id": run_id,
            "interrupt_id": interrupt_id or "",
            "interrupt_mode": interrupt_mode,
            "style": style,
        },
        key=key,
        on_done_change=lambda: None,
    )
    return result, run_id