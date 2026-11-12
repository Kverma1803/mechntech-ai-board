import os
import base64
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


def _get_logo_b64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def init_sidebar_state():
    if "sidebar_minimized" not in st.session_state:
        st.session_state.sidebar_minimized = False


def render_navbar():
    """
    Zeroes out Streamlit's top navbar, main top padding, and internal sidebar header padding,
    sets up a centered 80px minimized rail / 300px expanded Gemini-style sidebar, and pins
    the Login button to the bottom edge.
    """
    init_sidebar_state()
    minimized = st.session_state.sidebar_minimized
    sidebar_width = "80px" if minimized else "300px"

    st.markdown(
        f"""
        <style>
        /* 1. Remove Streamlit's top bar, toolbar & internal sidebar header height */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        div[data-testid="stSidebarHeader"],
        button[data-testid="stSidebarCollapseButton"],
        div[data-testid="stSidebarCollapsedControl"],
        div[data-testid="collapsedControl"] {{
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        /* Pull main workspace & heading flush to the top */
        div[data-testid="stMainBlockContainer"],
        section[data-testid="stMain"] > div.block-container,
        div[data-testid="stAppViewContainer"] > section.main > div.block-container,
        .block-container {{
            padding-top: 0.45rem !important;
            padding-left: 1.8rem !important;
            padding-right: 1.8rem !important;
            max-width: 100% !important;
        }}
        .hero-header h1,
        .hero-title {{
            padding-top: 0 !important;
            margin-top: 0 !important;
            line-height: 1.15 !important;
        }}

        /* 2. Permanent Gemini-Style Sidebar */
        section[data-testid="stSidebar"] {{
            width: {sidebar_width} !important;
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transform: none !important;
            margin-left: 0 !important;
            visibility: visible !important;
            background: #FFFFFF !important;
            border-right: 1px solid rgba(255, 107, 44, 0.16) !important;
            box-shadow: 4px 0 24px rgba(255, 107, 44, 0.05) !important;
            transition: width 0.2s ease, min-width 0.2s ease, max-width 0.2s ease !important;
            overflow: hidden !important;
        }}

        /* Make sidebar container span 100% viewport height without internal scrollbar */
        section[data-testid="stSidebar"] > div:first-child,
        div[data-testid="stSidebarContent"],
        div[data-testid="stSidebarUserContent"] {{
            height: 100vh !important;
            min-height: 100vh !important;
            padding-top: 0.75rem !important;
            padding-bottom: 1rem !important;
            padding-left: {"0px" if minimized else "0.9rem"} !important;
            padding-right: {"0px" if minimized else "0.9rem"} !important;
            width: 100% !important;
            overflow-x: hidden !important;
            overflow-y: {"hidden" if minimized else "auto"} !important;
            box-sizing: border-box !important;
        }}

        /* Stretch top-level vertical stack to full viewport height regardless of wrapper div */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div > div[data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] {{
            min-height: calc(100vh - 1.85rem) !important;
            height: calc(100vh - 1.85rem) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: {"center" if minimized else "stretch"} !important;
            gap: {"1.05rem" if minimized else "0.45rem"} !important;
        }}

        /* Pin ONLY the top-level last element (Login / API Setup button) to the bottom edge */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div > div[data-testid="stVerticalBlock"] > div:last-child,
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] > div:last-child {{
            margin-top: auto !important;
            padding-top: 0.75rem !important;
            border-top: 1px solid rgba(255, 107, 44, 0.16) !important;
        }}

        /* Center every element block inside the minimized sidebar */
        {"section[data-testid='stSidebar'] div[data-testid='stElementContainer'] { width: 100% !important; display: flex !important; justify-content: center !important; }" if minimized else ""}

        /* Expanded Brand Header */
        .gem-brand-row {{
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 2px 0 4px 0;
            white-space: nowrap;
        }}
        .gem-logo-expanded {{
            width: 44px;
            height: 44px;
            min-width: 44px;
            border-radius: 12px;
            object-fit: contain;
            background: #FFF8F4;
            padding: 4px;
            border: 1px solid rgba(255, 107, 44, 0.24);
        }}
        .gem-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: #18202C;
            letter-spacing: 0.2px;
        }}
        .gem-title span {{
            color: #FF5A1F;
        }}
        .gem-title-link {{
            text-decoration: none !important;
            color: inherit !important;
            display: inline-block;
            transition: opacity 0.15s ease;
        }}
        .gem-title-link:hover {{
            opacity: 0.82;
        }}

        /* Minimized Clickable Logo Card */
        .min-logo-wrap {{
            width: 52px;
            height: 52px;
            margin: 0 auto;
            border-radius: 15px;
            background: #FFF8F4;
            border: 1.5px solid rgba(255, 107, 44, 0.32);
            box-shadow: 0 4px 12px rgba(255, 90, 31, 0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .min-logo-wrap img {{
            width: 40px;
            height: 40px;
            object-fit: contain;
        }}

        /* Overlap transparent expand button directly on .min-logo-wrap with clean spacing below */
        div[data-testid="stElementContainer"]:has(.min-logo-wrap) + div[data-testid="stElementContainer"] {{
            margin-top: -68px !important;
            margin-bottom: 6px !important;
            height: 52px !important;
            z-index: 20 !important;
        }}
        div[data-testid="stElementContainer"]:has(.min-logo-wrap) + div[data-testid="stElementContainer"] button {{
            width: 52px !important;
            height: 52px !important;
            min-width: 52px !important;
            opacity: 0 !important;
            cursor: pointer !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        div[data-testid="stElementContainer"]:has(.min-logo-wrap):has(+ div[data-testid="stElementContainer"] button:hover) .min-logo-wrap {{
            border-color: #FF5A1F !important;
            transform: scale(1.05);
        }}

        /* Sidebar Navigation Buttons & Large Icon Sizing */
        section[data-testid="stSidebar"] .stButton {{
            width: {"52px" if minimized else "100%"} !important;
            display: flex !important;
            justify-content: center !important;
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if minimized else "flex-start"} !important;
            text-align: {"center" if minimized else "left"} !important;
            width: {"52px" if minimized else "100%"} !important;
            min-width: {"52px" if minimized else "auto"} !important;
            max-width: {"52px" if minimized else "100%"} !important;
            height: {"52px" if minimized else "auto"} !important;
            margin: 0 !important;
            padding: {"0" if minimized else "0.5rem 0.9rem"} !important;
            border-radius: {"15px" if minimized else "999px"} !important;
            border: 1px solid {"rgba(255, 107, 44, 0.16)" if minimized else "transparent"} !important;
            background: {"#FFFDFB" if minimized else "transparent"} !important;
            color: #1E293B !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            transition: all 0.15s ease !important;
        }}

        /* Target Streamlit's internal <p> tag so icons actually grow larger */
        section[data-testid="stSidebar"] .stButton > button p {{
            font-size: {"1.55rem" if minimized else "0.96rem"} !important;
            line-height: 1 !important;
            margin: 0 !important;
        }}

        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: #FFF3EB !important;
            color: #D9480F !important;
            border-color: rgba(255, 107, 44, 0.35) !important;
            transform: {"scale(1.04)" if minimized else "none"};
        }}

        .gem-section-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #94A3B8;
            margin: 12px 0 6px 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header():
    """
    Renders the top MechnTechAI brand row:
    - Minimized: Single 52x52 logo card — clicking directly on the logo expands the sidebar.
    - Expanded: 44x44 logo + clickable 'MechnTechAI' link + '«' minimize button.
    """
    init_sidebar_state()
    minimized = st.session_state.sidebar_minimized
    logo_b64 = _get_logo_b64()

    logo_img = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="MechnTechAI"/>'
        if logo_b64
        else '<span style="font-weight:800;font-size:1.15rem;color:#FF5A1F;">MT</span>'
    )

    if minimized:
        st.markdown(f'<div class="min-logo-wrap">{logo_img}</div>', unsafe_allow_html=True)
        if st.button(" ", key="expand_on_logo_click", help="Click logo to expand MechnTechAI"):
            st.session_state.sidebar_minimized = False
            st.rerun()
        st.markdown("<hr style='width:44px; margin: 2px auto 2px auto; border-color: rgba(255,107,44,0.2);'/>", unsafe_allow_html=True)
    else:
        logo_expanded = (
            f'<img src="data:image/png;base64,{logo_b64}" class="gem-logo-expanded" alt="MechnTechAI"/>'
            if logo_b64
            else '<div class="gem-logo-expanded" style="display:flex;align-items:center;justify-content:center;font-weight:800;color:#FF5A1F;">MT</div>'
        )
        col_brand, col_btn = st.columns([4.4, 1])
        with col_brand:
            st.markdown(
                f"""
                <div class="gem-brand-row">
                    {logo_expanded}
                    <a href="https://mech-n-tech.vercel.app/" target="_blank" rel="noopener noreferrer" class="gem-title-link">
                        <div class="gem-title">MechnTech<span>AI</span></div>
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_btn:
            if st.button("«", key="minimize_sidebar_btn", help="Minimize Sidebar"):
                st.session_state.sidebar_minimized = True
                st.rerun()
        st.markdown("<hr style='margin: 2px 0 10px 0; border-color: rgba(255,107,44,0.14);'/>", unsafe_allow_html=True)