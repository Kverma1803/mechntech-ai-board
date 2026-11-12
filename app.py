import os
import time
import json
import docx
import streamlit as st
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from agents import (
    BASE_DIR,
    CONFIG_FILE,
    load_ai_config,
    save_ai_config,
    run_specialist_agent,
    run_chief_engineer,
)
from file_processing import process_uploaded_files
from mech_3d_widget import render_mech_3d_hud
from navbar_widget import render_navbar, render_sidebar_header

load_dotenv()

HISTORY_FILE = os.path.join(BASE_DIR, "review_history.json")

st.set_page_config(
    page_title="MechnTechAI — Engineering Board",
    layout="wide",
    initial_sidebar_state="expanded",
)
render_navbar()

# --- SESSION STATE INITIALIZATION ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "board"  # "board" | "setup"
if "active_results" not in st.session_state:
    st.session_state.active_results = None
if "active_product_name" not in st.session_state:
    st.session_state.active_product_name = ""


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_to_history(prod_title, results_dict):
    history = load_history()
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "title": prod_title.strip() or f"Design Review ({datetime.now().strftime('%d %b, %H:%M')})",
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "results": results_dict,
    }
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:20], f, indent=4)


# --- GLOBAL CSS: Warm White & Orange Gradient + Rounded Corners ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F5 48%, #FFEFE4 100%);
        color: #1E2430;
    }

    iframe[title="streamlit_components_v1.html"],
    iframe {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 107, 44, 0.25) !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(255, 107, 44, 0.04);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FF6B2C !important;
        box-shadow: 0 0 0 2px rgba(255, 107, 44, 0.18) !important;
    }

    section[data-testid="stFileUploader"] > div {
        border-radius: 16px !important;
        border: 1.5px dashed rgba(255, 107, 44, 0.4) !important;
        background-color: #FFFBF8 !important;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        background: linear-gradient(90deg, #FF5A1F 0%, #FF8A00 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 6px 18px rgba(255, 90, 31, 0.28) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 22px !important;
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid rgba(255, 107, 44, 0.18) !important;
        box-shadow: 0 10px 30px rgba(255, 107, 44, 0.07) !important;
        padding: 1rem !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 107, 44, 0.22) !important;
        background-color: #FFF6F0 !important;
        color: #7C2D12 !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 6px 14px !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFE8D9 !important;
        color: #D9480F !important;
    }

    .hero-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0;
        margin-bottom: 0.65rem;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #18202C;
        margin: 0;
    }
    .hero-title span {
        background: linear-gradient(90deg, #FF5A1F 0%, #FF9500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-badge {
        background: #FFF0E6;
        color: #D9480F;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid rgba(255, 107, 44, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

config = load_ai_config()
active_provider = config["active_provider"]
active_model = config["providers"][active_provider]["model"]

# --- GEMINI-STYLE PERMANENT COLLAPSIBLE SIDEBAR ---
with st.sidebar:
    render_sidebar_header()
    is_min = st.session_state.get("sidebar_minimized", False)

    # 1. New Review (New Chat)
    new_label = "✏️" if is_min else "✏️  New Engineering Review"
    if st.button(new_label, key="nav_new_review", help="Start a New Engineering Review", use_container_width=True):
        st.session_state.current_page = "board"
        st.session_state.active_results = None
        st.session_state.active_product_name = ""
        st.rerun()

    # 2. Design Files Uploader (Only shown when sidebar is expanded)
    uploaded_files = None
    if not is_min:
        with st.expander("📎  Upload CAD / Spec Files", expanded=False):
            uploaded_files = st.file_uploader(
                "PDF, DOCX, CSV, XLSX, TXT, JPG, PNG",
                accept_multiple_files=True,
                label_visibility="collapsed",
            )

    # 3. History Section
    if is_min:
        if st.button("🕒", key="nav_hist_min", help="View Recent Reviews History", use_container_width=True):
            st.session_state.sidebar_minimized = False
            st.rerun()
    else:
        st.markdown('<div class="gem-section-label">Recent Reviews</div>', unsafe_allow_html=True)
        history_items = load_history()
        if not history_items:
            st.caption("No past reviews yet.")
        else:
            for item in history_items[:8]:
                if st.button(f"📄  {item['title'][:25]}", key=f"hist_{item['id']}", use_container_width=True):
                    st.session_state.current_page = "board"
                    st.session_state.active_results = item["results"]
                    st.session_state.active_product_name = item["title"]
                    st.rerun()

    # 4. Bottom-most Login / API & Model Setup Button (Pinned to bottom by CSS :last-child)
    active_key_check = config["providers"][active_provider]["api_key"].strip()
    is_logged_in = bool(active_key_check) and not active_key_check.startswith("PASTE_YOUR_")

    if is_min:
        login_btn_text = "🔐" if is_logged_in else "🔑"
    else:
        login_btn_text = f"🔐  Login / API Setup ({active_provider})" if is_logged_in else "🔑  Login / API & Model Setup"

    if st.button(login_btn_text, key="nav_login_setup", help="Open API & Model Setup", use_container_width=True):
        st.session_state.current_page = "setup"
        st.rerun()


def generate_docx(results):
    doc = docx.Document()
    doc.add_heading("MechnTechAI - Consolidated Engineering Report", 0)
    for agent, text in results.items():
        doc.add_heading(agent, level=1)
        for line in text.split("\n"):
            doc.add_paragraph(line)
    b = BytesIO()
    doc.save(b)
    return b.getvalue()


# ==============================================================================
# PAGE 1: LOGIN / API & MODEL SETUP PAGE (Triggered from Bottom Sidebar Button)
# ==============================================================================
if st.session_state.current_page == "setup":
    st.markdown(
        """
        <div class="hero-header">
            <div>
                <h1 class="hero-title">API & <span>Model Setup</span></h1>
                <div style="color:#5A6475; font-size:0.9rem;">Connect your AI provider key, choose the engineering model, and configure rate-limit delays.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Back to Engineering Board"):
        st.session_state.current_page = "board"
        st.rerun()

    setup_col1, setup_col2 = st.columns([1.2, 1], gap="large")

    with setup_col1:
        with st.container(border=True):
            st.markdown("#### 🔐 Provider Authentication & Model Selection")
            provider_names = list(config["providers"].keys())
            selected_provider = st.selectbox(
                "Active AI Provider",
                options=provider_names,
                index=provider_names.index(config["active_provider"]),
            )
            provider_details = config["providers"][selected_provider]

            api_key_input = st.text_input(
                f"{selected_provider} API Key",
                type="password",
                value="" if provider_details["api_key"].startswith("PASTE_YOUR_") else provider_details["api_key"],
                placeholder="Paste your API key here (e.g., gsk_... or AIza...)",
            )

            available_models = provider_details.get("models", {})
            model_options = list(available_models.keys()) + ["Custom Model ID..."]
            saved_model = provider_details.get("model", "")
            default_idx = model_options.index(saved_model) if saved_model in model_options else 0

            selected_model_option = st.selectbox(
                "Select Model",
                options=model_options,
                index=default_idx,
            )

            if selected_model_option == "Custom Model ID...":
                model_input = st.text_input("Enter Custom Model ID", value=saved_model)
            else:
                model_input = selected_model_option
                st.info(f"**When to use `{model_input}`:**\n\n{available_models[model_input]}")

            delay_input = st.number_input(
                "Delay Between Agents (sec)",
                min_value=0,
                max_value=60,
                value=int(provider_details.get("delay_seconds", 10)),
            )
            st.caption(
                "**Why delay helps:** Pauses between calls so free-tier token quotas reset, "
                "preventing `429 Rate Limit` errors. *(Recommended: **45s** Groq Vision, **5s** Groq Text, **2s** Gemini, **0s** OpenAI.)*"
            )

            if st.button("Save & Activate Engine →", type="primary", use_container_width=True):
                config["active_provider"] = selected_provider
                if api_key_input.strip():
                    config["providers"][selected_provider]["api_key"] = api_key_input.strip()
                config["providers"][selected_provider]["model"] = model_input.strip()
                config["providers"][selected_provider]["delay_seconds"] = delay_input
                save_ai_config(config)
                st.success(f"Connected to {selected_provider} ({model_input})!")
                time.sleep(0.6)
                st.session_state.current_page = "board"
                st.rerun()

    with setup_col2:
        with st.container(border=True):
            st.markdown("#### 🛠️ Advanced Configuration (`ai_config.txt`)")
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw_cfg = f.read()
            edited_raw = st.text_area("Raw JSON Config", value=raw_cfg, height=340)
            if st.button("Save Raw JSON File", use_container_width=True):
                try:
                    parsed = json.loads(edited_raw)
                    save_ai_config(parsed)
                    st.success("ai_config.txt updated successfully!")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON format: {e}")


# ==============================================================================
# PAGE 2: MAIN ENGINEERING REVIEW BOARD WORKSPACE
# ==============================================================================
else:
    st.markdown(
        f"""
        <div class="hero-header">
            <div>
                <h1 class="hero-title">AI <span>Engineering</span> Board</h1>
                <div style="color:#5A6475; font-size:0.9rem;">Preliminary multi-agent hardware & mechanical design review — requires qualified engineer sign-off.</div>
            </div>
            <div class="hero-badge">● {active_provider} · {active_model}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.05, 1.2], gap="large")

    with left_col:
        with st.container(border=True):
            st.markdown("#### 📋 Project Parameters & Prompts")
            c1, c2 = st.columns(2)
            with c1:
                prod_name = st.text_input("Product Name", value=st.session_state.active_product_name, placeholder="e.g., Servo Bracket SMB-400")
                materials = st.text_input("Materials", placeholder="e.g., 6061-T6 Aluminum")
                dimensions = st.text_input("Dimensions", placeholder="e.g., 140 x 120 x 8 mm")
                prod_desc = st.text_area("Product Description", height=85)
                reqs = st.text_area("Design Requirements", height=85)
                op_cond = st.text_area("Operating Conditions", height=85)
            with c2:
                standards = st.text_input("Applicable Standards", placeholder="e.g., ISO 2768-m, ISO 12100")
                mfg_process = st.text_input("Manufacturing Process", placeholder="e.g., 3-Axis CNC Milling")
                cost_targets = st.text_input("Cost Targets", placeholder="e.g., ₹1,200 / unit")
                loads = st.text_area("Loads & Boundary Conditions", height=85)
                add_instr = st.text_area("Additional Instructions", height=195)

            run_clicked = st.button("Run Complete Engineering Review →", type="primary", use_container_width=True)

    with right_col:
        hud_slot = st.empty()
        initial_state = "READY" if st.session_state.active_results else "IDLE"
        with hud_slot:
            render_mech_3d_hud(state=initial_state, active_agent="Report Loaded" if st.session_state.active_results else "Standby")

        with st.container(border=True):
            st.markdown("#### 📊 Live Engineering Report Card")
            progress_slot = st.empty()
            report_area = st.empty()

            # Show loaded history report if user clicked a past review from sidebar
            if not run_clicked and st.session_state.active_results:
                saved_res = st.session_state.active_results
                agents_list = [
                    "Design Engineer",
                    "DFM Engineer",
                    "Simulation Engineer",
                    "Manufacturing Engineer",
                    "Testing and Validation Engineer",
                    "DFMEA Engineer",
                ]
                with report_area.container():
                    tabs = st.tabs(agents_list + ["Chief Manager", "Download"])
                    for idx, ag in enumerate(agents_list):
                        with tabs[idx]:
                            st.markdown(saved_res.get(ag, "_No data recorded._"))
                    with tabs[6]:
                        st.markdown(saved_res.get("Chief Engineering Manager", "_No data recorded._"))
                    with tabs[7]:
                        docx_data = generate_docx(saved_res)
                        st.download_button(
                            label="Download Consolidated Report (.docx)",
                            data=docx_data,
                            file_name=f"{st.session_state.active_product_name.replace(' ', '_') or 'Engineering'}_Report.docx",
                            use_container_width=True,
                        )
            elif not run_clicked:
                with report_area.container():
                    st.info(
                        "Fill out your project parameters on the left (or upload CAD drawings in the sidebar) "
                        "and click **Run Complete Engineering Review →** to watch all 6 specialists and the "
                        "Chief Engineering Manager populate this card live."
                    )

    if run_clicked:
        latest_config = load_ai_config()
        curr_provider = latest_config["active_provider"]
        active_key = latest_config["providers"][curr_provider]["api_key"].strip()
        delay_sec = latest_config["providers"][curr_provider].get("delay_seconds", 0)

        if not active_key or active_key.startswith("PASTE_YOUR_"):
            st.warning("No API key configured yet. Redirecting to Login / API & Model Setup...")
            time.sleep(0.8)
            st.session_state.current_page = "setup"
            st.rerun()

        with hud_slot:
            render_mech_3d_hud(state="WORKING", active_agent="Extracting Files", step_info="0/7")

        with st.spinner("Extracting information from uploaded files..."):
            file_text, images_b64 = process_uploaded_files(uploaded_files or [])

        context = f"""
        Product Name: {prod_name}
        Description: {prod_desc}
        Requirements: {reqs}
        Operating Conditions: {op_cond}
        Materials: {materials}
        Dimensions: {dimensions}
        Loads: {loads}
        Standards: {standards}
        Mfg Process: {mfg_process}
        Cost Targets: {cost_targets}
        Instructions: {add_instr}

        EXTRACTED FILE DATA:
        {file_text}
        """

        agents_list = [
            "Design Engineer",
            "DFM Engineer",
            "Simulation Engineer",
            "Manufacturing Engineer",
            "Testing and Validation Engineer",
            "DFMEA Engineer",
        ]

        results = {}
        progress_bar = progress_slot.progress(0)

        with report_area.container():
            tabs = st.tabs(agents_list + ["Chief Manager", "Download"])

            for i, agent in enumerate(agents_list):
                with hud_slot:
                    render_mech_3d_hud(state="WORKING", active_agent=agent, step_info=f"{i + 1}/7")

                with tabs[i]:
                    with st.spinner(f"{agent} is analyzing..."):
                        try:
                            res = run_specialist_agent(agent, context, images_b64)
                            results[agent] = res
                            st.markdown(res)
                        except Exception as e:
                            st.error(f"Error executing {agent}: {e}")

                progress_bar.progress((i + 1) / 7)
                if delay_sec > 0:
                    with hud_slot:
                        render_mech_3d_hud(
                            state="WORKING",
                            active_agent=f"Cooldown ({delay_sec}s)",
                            step_info=f"{i + 1}/7",
                        )
                    time.sleep(delay_sec)

            with hud_slot:
                render_mech_3d_hud(state="WORKING", active_agent="Chief Engineering Manager", step_info="7/7")

            with tabs[6]:
                with st.spinner("Chief Engineering Manager is synthesizing findings..."):
                    try:
                        chief_res = run_chief_engineer(context, results, images_b64)
                        results["Chief Engineering Manager"] = chief_res
                        st.markdown(chief_res)
                    except Exception as e:
                        st.error(f"Error executing Chief Engineer: {e}")

            progress_bar.progress(1.0)
            st.session_state.active_results = results
            st.session_state.active_product_name = prod_name
            save_to_history(prod_name, results)

            with hud_slot:
                render_mech_3d_hud(state="READY", active_agent="Report Ready", step_info="7/7")

            with tabs[7]:
                st.success("All 7 reviews completed and saved to History!")
                docx_data = generate_docx(results)
                st.download_button(
                    label="Download Consolidated Report (.docx)",
                    data=docx_data,
                    file_name=f"{prod_name.replace(' ', '_') or 'Engineering'}_Report.docx",
                    use_container_width=True,
                )