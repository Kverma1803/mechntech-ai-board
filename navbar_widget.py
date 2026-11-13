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
        st.session_state.sidebar_minimized = True


def render_navbar():
    """
    Locks light theme, removes Streamlit's top header, sets up the Gemini-style
    collapsible sidebar (starts minimized), and enforces pixel-aligned button symmetry.
    """
    init_sidebar_state()
    minimized = st.session_state.sidebar_minimized
    sidebar_width = "80px" if minimized else "300px"
    mobile_sidebar_width = "72px" if minimized else "82vw"
    mobile_sidebar_max = "72px" if minimized else "310px"

    st.markdown(
        f"""
        <style>
        /* 1. Force Light Mode & Hide Streamlit Chrome */
        :root {{
            color-scheme: light !important;
        }}

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

        /* Force light inputs & text across mobile dark-mode browsers */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input,
        div[data-baseweb="select"] > div {{
            background-color: #FFFFFF !important;
            color: #1E2430 !important;
        }}

        /* 2. Main Workspace Padding (Desktop) */
        div[data-testid="stMainBlockContainer"],
        section[data-testid="stMain"] > div.block-container,
        div[data-testid="stAppViewContainer"] > section.main > div.block-container,
        .block-container {{
            padding-top: 0.55rem !important;
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

        /* 3. Permanent Gemini-Style Sidebar */
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
            z-index: 9999 !important;
        }}

        /* 4. Mobile & Narrow Viewport Responsive Rules */
        @media (max-width: 767px) {{
            section[data-testid="stSidebar"] {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: {mobile_sidebar_width} !important;
                min-width: {mobile_sidebar_width} !important;
                max-width: {mobile_sidebar_max} !important;
                box-shadow: 10px 0 32px rgba(15, 23, 42, 0.18) !important;
            }}

            div[data-testid="stMainBlockContainer"],
            section[data-testid="stMain"] > div.block-container,
            div[data-testid="stAppViewContainer"] > section.main > div.block-container,
            .block-container {{
                padding-top: 0.65rem !important;
                padding-left: calc(72px + 0.95rem) !important;
                padding-right: 0.85rem !important;
                max-width: 100% !important;
            }}

            .hero-header {{
                flex-direction: column !important;
                align-items: flex-start !important;
                gap: 6px !important;
            }}

            .hero-title {{
                font-size: 1.4rem !important;
            }}
        }}

        /* Sidebar Internal Layout */
        section[data-testid="stSidebar"] > div:first-child,
        div[data-testid="stSidebarContent"],
        div[data-testid="stSidebarUserContent"] {{
            height: 100vh !important;
            min-height: 100vh !important;
            padding-top: 0.85rem !important;
            padding-bottom: 1rem !important;
            padding-left: {"0px" if minimized else "0.95rem"} !important;
            padding-right: {"0px" if minimized else "0.95rem"} !important;
            width: 100% !important;
            overflow-x: hidden !important;
            overflow-y: {"hidden" if minimized else "auto"} !important;
            box-sizing: border-box !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div > div[data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] {{
            min-height: calc(100vh - 1.95rem) !important;
            height: calc(100vh - 1.95rem) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: {"center" if minimized else "stretch"} !important;
            gap: {"1.05rem" if minimized else "0.55rem"} !important;
        }}

        /* Force Full 100% Width on All Expanded Sidebar Containers */
        {"section[data-testid='stSidebar'] div[data-testid='stElementContainer'] { width: 100% !important; display: flex !important; justify-content: center !important; }" if minimized else "section[data-testid='stSidebar'] div[data-testid='stVerticalBlock'] > div[data-testid='stElementContainer'] { width: 100% !important; max-width: 100% !important; }"}

        /* Pin Bottom Login / API Setup Button */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div > div[data-testid="stVerticalBlock"] > div:last-child,
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlock"] > div:last-child {{
            margin-top: auto !important;
            padding-top: 0.85rem !important;
            border-top: 1px solid rgba(255, 107, 44, 0.16) !important;
            width: {"auto" if minimized else "100%"} !important;
        }}

        /* Pixel-Perfect Top Header Alignment ('MT' + 'MechnTechAI' + '«') */
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 8px !important;
            width: 100% !important;
            min-height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {{
            flex: 1 1 auto !important;
            width: auto !important;
            min-width: 0 !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {{
            flex: 0 0 38px !important;
            width: 38px !important;
            min-width: 38px !important;
            max-width: 38px !important;
            justify-content: flex-end !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stElementContainer"],
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stMarkdownContainer"] {{
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            width: auto !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] div[data-testid="stButton"],
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] .stButton,
        section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button {{
            width: 38px !important;
            min-width: 38px !important;
            max-width: 38px !important;
            height: 38px !important;
            min-height: 38px !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 107, 44, 0.24) !important;
            background: #FFF8F4 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }}

        /* Expanded Brand Header */
        .gem-brand-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            height: 38px;
            margin: 0;
            padding: 0;
            white-space: nowrap;
        }}
        .gem-logo-expanded {{
            width: 38px;
            height: 38px;
            min-width: 38px;
            border-radius: 10px;
            object-fit: contain;
            background: #FFF8F4;
            padding: 4px;
            border: 1px solid rgba(255, 107, 44, 0.24);
            box-sizing: border-box;
        }}
        .gem-title {{
            font-size: 1.12rem;
            font-weight: 800;
            color: #18202C;
            letter-spacing: 0.2px;
            line-height: 1;
        }}
        .gem-title span {{
            color: #FF5A1F;
        }}
        .gem-title-link {{
            text-decoration: none !important;
            color: inherit !important;
            display: inline-flex;
            align-items: center;
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

        /* Full-Width Uniform Navigation Buttons */
        section[data-testid="stSidebar"] div[data-testid="stButton"],
        section[data-testid="stSidebar"] .stButton {{
            width: {"52px" if minimized else "100%"} !important;
            max-width: {"52px" if minimized else "100%"} !important;
            display: flex !important;
            justify-content: {"center" if minimized else "flex-start"} !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
        section[data-testid="stSidebar"] .stButton > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if minimized else "flex-start"} !important;
            text-align: {"center" if minimized else "left"} !important;
            width: {"52px" if minimized else "100%"} !important;
            min-width: {"52px" if minimized else "100%"} !important;
            max-width: {"52px" if minimized else "100%"} !important;
            height: {"52px" if minimized else "44px"} !important;
            margin: 0 !important;
            padding: {"0" if minimized else "0 0.85rem"} !important;
            border-radius: {"15px" if minimized else "12px"} !important;
            border: 1px solid {"rgba(255, 107, 44, 0.18)" if minimized else "rgba(255, 107, 44, 0.22)"} !important;
            background: {"#FFFDFB" if minimized else "#FFFDFB"} !important;
            color: #1E293B !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            transition: all 0.15s ease !important;
            box-sizing: border-box !important;
        }}
        section[data-testid="stSidebar"] .stButton > button > div {{
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if minimized else "flex-start"} !important;
        }}
        section[data-testid="stSidebar"] .stButton > button p {{
            font-size: {"1.55rem" if minimized else "0.93rem"} !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            text-align: {"center" if minimized else "left"} !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: #FFF3EB !important;
            color: #D9480F !important;
            border-color: rgba(255, 107, 44, 0.4) !important;
            transform: {"scale(1.04)" if minimized else "none"};
        }}

        /* Matching Full-Width Expander Styling */
        section[data-testid="stSidebar"] div[data-testid="stExpander"],
        section[data-testid="stSidebar"] details {{
            width: 100% !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 107, 44, 0.22) !important;
            background: #FFFBF8 !important;
            box-sizing: border-box !important;
        }}
        section[data-testid="stSidebar"] details summary {{
            min-height: 44px !important;
            padding: 0 0.85rem !important;
            display: flex !important;
            align-items: center !important;
            font-size: 0.93rem !important;
            white-space: nowrap !important;
        }}

        .gem-section-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #94A3B8;
            margin: 10px 0 2px 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header():
    """
    Renders the top MechnTechAI brand row:
    - Minimized: Single 52x52 logo card — clicking directly on the logo expands the sidebar.
    - Expanded: 38x38 logo + clickable 'MechnTechAI' link + inline '«' minimize button.
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
        st.markdown("<hr style='margin: 8px 0 8px 0; border-color: rgba(255,107,44,0.14);'/>", unsafe_allow_html=True)