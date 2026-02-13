import streamlit as st


def configure_sidebar(
    page_title: str = "App",
    layout: str = "wide",
    expanded: bool = True,
    lock: bool = True,
    width_px: int = 420,   # ← NEW: sidebar width control
):
    """
    Configure sidebar behavior.

    Parameters
    ----------
    page_title : str
        Browser tab title.
    layout : str
        "wide" or "centered"
    expanded : bool
        If True, sidebar is expanded by default.
    lock : bool
        If True, hides collapse button (prevents folding).
    width_px : int
        Sidebar width in pixels.
    """

    # -------------------------
    # Page config (MUST be first st call)
    # -------------------------
    st.set_page_config(
        page_title=page_title,
        layout=layout,
        initial_sidebar_state="expanded" if expanded else "collapsed",
    )

    # -------------------------
    # CSS overrides
    # -------------------------
    css = f"""
    <style>
        /* Set sidebar width */
        section[data-testid="stSidebar"] {{
            width: {width_px}px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            width: {width_px}px !important;
        }}
    """

    # Lock collapse button if requested
    if lock:
        css += """
        /* Hide sidebar collapse button */
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        /* Backup selector (some versions) */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        """

    css += "</style>"

    st.markdown(css, unsafe_allow_html=True)