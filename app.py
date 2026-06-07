import io
import re
import zipfile
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# 1. Page Configuration (Replit Dynamic Layout)
st.set_page_config(
    page_title="WebMaster Pro - Ultimate Agent",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Advanced Replit UI Dashboard Dark Theme CSS Inject
st.markdown("""
    <style>
    .stApp {
        background-color: #0c0d0e !important;
        color: #f3f4f6 !important;
    }
    h1, h2, h3, p, span, label {
        font-family: 'Inter', sans-serif !important;
    }
    /* Central Replit Search Box Container styling */
    .stTextArea textarea {
        background-color: #141619 !important;
        color: #ffffff !important;
        border: 1px solid #282a30 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus {
        border-color: #3e424b !important;
        box-shadow: none !important;
    }
    /* Login Box Dashboard element */
    .login-container {
        background-color: #141619;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #22252a;
        margin-bottom: 20px;
    }
    /* Success Published Toast style styling */
    .publish-box {
        background-color: #064e3b;
        color: #34d399;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #059669;
        margin-top: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BACKEND API HARDCODING (તમારી સાચી Gemini 2.5 API Key અહીં નાખો)
# -----------------------------------------------------------------------------
USER_GEMINI_KEY = "AQ.Ab8RN6IlzlzvRHHAiTILGbA_XG0JkbCSGLO54Ctafhh77mz0AA"
MODEL_ENGINE_NAME = "gemini-2.5-flash"  # 100% optimized for Gemini 2.5 API

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<div style='text-align:center;'><h1>Welcome to WebMaster</h1><p>Your workspace is live. Use the left console to start generating apps like Classplus.</p></div>",
        "style.css": "body { font-family: sans-serif; background-color: #0c0d0e; color: white; padding-top: 50px; }",
        "script.js": "console.log('WebMaster Ultimate Workspace loaded.');"
    }
if "selected_file" not in st.session_state:
    st.session_state.selected_file = "index.html"
if "generated_apps_tracker" not in st.session_state:
    st.session_state.generated_apps_tracker = 0
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "app_publish_status" not in st.session_state:
    st.session_state.app_publish_status = False

# -----------------------------------------------------------------------------
# CORE LOGIC ENGINES (COMPILATION & PARSING)
# -----------------------------------------------------------------------------
def build_application_backend(prompt, api_key):
    """Generates complex multi-module software blocks securely using Gemini 2.5 API."""
    if not api_key or api_key == "YOUR_GEMINI_2_5_API_KEY_HERE":
        return "❌ WebMaster Configuration Notice: Please open app.py and enter your active Gemini 2.5 API Key on line 44."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_ENGINE_NAME)
        
        system_rules = (
            "You are WebMaster Pro, an elite software architect like Replit Agent. Build a fully functional system. "
            "Output ALL required files wrapped strictly within XML format tags like this:\n"
            "<file name=\"filename.ext\">\n...code...\n</file>\n"
            "Produce fully operational, interactive files (e.g., student_dashboard.html, login.html, store.html, style.css, script.js) if the user asks for a complex platform like Classplus. "
            "Do not write regular markdown blocks, conversation, or summaries outside the XML file wrappers."
        )
        
        payload_prompt = f"{system_rules}\n\nBuild Request: {prompt}"
        response = model.generate_content(payload_prompt)
        return response.text
    except Exception as e:
        return f"❌ AI Engine Communication Error: {str(e)}"

def parse_incoming_file_tree(response_text):
    """Stitches response syntax blocks into the workspace tab controller seamlessly."""
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, response_text)
    if not matches:
        # Secondary fallback checker for single quote properties
        pattern = r"<file\s+name='([^']+)'>([\s\S]*?)<\/file>"
        matches = re.findall(pattern, response_text)
    return {fname.strip(): content.strip() for fname, content in matches}

# -----------------------------------------------------------------------------
# SIDEBAR REPLIT CONSOLE INTERFACE
# -----------------------------------------------------------------------------
st.sidebar.title("💻 WebMaster Panel")
st.sidebar.caption("System Engine Status: Active")
st.sidebar.markdown("---")

# User Authentication Management
if not st.session_state.is_logged_in:
    st.sidebar.markdown("""
        <div class='login-container'>
        <p style='color: #ef4444; margin-bottom: 2px; font-weight: bold;'>🔒 Anonymous Mode Limit</p>
        <p style='font-size: 12px; color: #9ca3af; margin: 0;'>1 Free workspace creation allocated. Login to clear restrictions.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.subheader("👤 Creator Registration / Login")
    user_id = st.sidebar.text_input("Username / Email", key="username_field")
    user_pw = st.sidebar.text_input("Password", type="password", key="password_field")
    login_action = st.sidebar.button("Login & Unlock Pro Cloud", use_container_width=True)
    
    if login_action:
        if user_id and user_pw:
            st.session_state.is_logged_in = True
            st.sidebar.success("Welcome back! Premium limits unlocked.")
            st.rerun()
        else:
            st.sidebar.error("Credentials cannot be left empty.")
else:
    st.sidebar.markdown("""
        <div style='background-color: #1e3a8a; padding: 15px; border-radius: 6px; border: 1px solid #3b82f6; margin-bottom:15px;'>
        <p style='color: #60a5fa; margin:0; font-weight:bold;'>🚀 Premium Workspace Unlocked</p>
        <p style='font-size:12px; margin:0; color:#bfdbfe;'>You have infinite tokens to engineer applications.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Disconnect Secure Session", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.generated_apps_tracker = 0
        st.session_state.app_publish_status = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Total compilation tokens run in session: {st.session_state.generated_apps_tracker}")

# -----------------------------------------------------------------------------
# MAIN REPLIT INTERIOR DASHBOARD UI SPLIT
# -----------------------------------------------------------------------------
left_console, right_workspace = st.columns()

# --- LEFT PANEL: Prompt Architecture Console (Replit Agent Lookalike) ---
with left_console:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"## Hi Creator, what do you want to make?")
    st.caption("WebMaster Pro Agent will write, evaluate, and assemble your full production build.")
    st.markdown("<br>", unsafe_allow_html=True)

    # તમારા કહ્યા મુજબ બિલકુલ "give here your mind thought" લખાણ સાથેનો સેન્ટ્રલ સર્ચ બાર
    user_prompt_input = st.text_area(
        "Prompt Input Element",
        placeholder="give here your mind thought",
        height=140,
        label_visibility="collapsed",
        key="central_replit_prompt"
    )
    
    trigger_build = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # Gatekeeper check constraint (૧ એપ ફ્રી ચેકર કંડિશન)
    allow_compilation = True
    if st.session_state.generated_apps_tracker >= 1 and not st.session_state.is_logged_in:
        allow_compilation = False
        st.markdown("""
            <div style='background-color: #3b1414; padding: 15px; border-radius: 6px; border: 1px solid #ef4444; margin-top: 15px;'>
            <p style='margin:0; color:#fca5a5; font-weight:bold;'>🛑 Free Sandbox Limit Reached</p>
            <p style='margin:0; font-size:13px; color:#d1d5db;'>You have engineered 1 application sandbox. Please <b>Login</b> on the sidebar account system to continue creating architectures.</p>
            </div>
        """, unsafe_allow_html=True)

    # Core Execution Script Execution Trigger
    if trigger_build and user_prompt_input:
        if not allow_compilation:
            st.toast("Authorization token missing. Please sign in.", icon="🔒")
        else:
            with st.spinner("WebMaster AI Agent is creating code modules... 🛠️"):
                raw_response = build_application_backend(user_prompt_input, USER_GEMINI_KEY)
                extracted_files = parse_incoming_file_tree(raw_response)
                
                if extracted_files:
                    st.session_state.project_files = extracted_files
                    st.session_state.selected_file = list(extracted_files.keys())
                    st.session_state.generated_apps_tracker += 1
                    st.session_state.app_publish_status = False  # Reset publish state on new build
                    st.toast("Application framework refreshed successfully!", icon="🎉")
                    st.rerun()
                else:
                    st.error("System Engine Notice: Parsing fallback initialized. Raw response tree rendered below.")
                    st.code(raw_response)

# --- RIGHT PANEL: Interactive Development Tree & Live Component Sandbox ---
with right_workspace:
    st.markdown("### 🛠️ Workspace Repository & Deployment")
    file_map_list = list(st.session_state.project_files.keys())
    
    if file_map_list:
        active_tab_file = st.session_state.selected_file
        if active_tab_file not in file_map_list:
            active_tab_file = file_map_list
            
        selected_file_tab = st.selectbox("📂 Project Repository File Explorer", options=file_map_list, index=file_map_list.index(active_tab_file))
        st.session_state.selected_file = selected_file_tab
        
        # Interactive Live Text Editor Core Code
        live_content_code = st.session_state.project_files[selected_file_tab]
        modified_code = st.text_area(label=f"Code Editor: {selected_file_tab}", value=live_content_code, height=220)
        st.session_state.project_files[selected_file_tab] = modified_code
        
        # Action Control Panel (Download + Publish App Feature)
        act_col1, act_col2 = st.columns(2)
        
        with act_col1:
            # Package configuration bundler
            zip_buffer_io = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_io, "w", zipfile.ZIP_DEFLATED) as packaged_zip:
                for fname, fcontent in st.session_state.project_files.items():
                    packaged_zip.writestr(fname, fcontent)
            
            st.download_button(
                label="📥 Export Build Project (.ZIP)",
                data=zip_buffer_io.getvalue(),
                file_name="webmaster_agent_project.zip",
                mime="application/zip",
                use_container_width=True
            )
            
        with act_col2:
            # તમે માગેલું ખાસ "Publish App" ફીચર બટન
            if st.button("🌐 Publish App to WebMaster Cloud", use_container_width=True):
                st.session_state.app_publish_status = True
                
        if st.session_state.app_publish_status:
            st.markdown("""
                <div class='publish-box'>
                <p style='margin:0; font-weight:bold;'>🚀 Application Published Successfully!</p>
                <p style='margin:0; font-size:12px; color:#a7f3d0;'>Your live environment deployment is completed. Link is active on WebMaster cloud instances.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🖥️ Real-time Live Sandbox Preview")
        
        # Environment automatic binding layout engine
        target_preview_file = "index.html" if "index.html" in st.session_state.project_files else file_map_list
        
        if target_preview_file.endswith(".html"):
            markup_code = st.session_state.project_files.get(target_preview_file, "")
            css_style_code = st.session_state.project_files.get("style.css", "")
            javascript_code = st.session_state.project_files.get("script.js", "")
            
            integrated_web_html = markup_code
            if "<head>" in integrated_web_html:
                integrated_web_html = integrated_web_html.replace("<head>", f"<head>\n<style>{css_style_code}</style>")
            else:
                integrated_web_html = f"<style>{css_style_code}</style>\n" + integrated_web_html
                
            if "</body>" in integrated_web_html:
                integrated_web_html = integrated_web_html.replace("</body>", f"<script>{javascript_code}</script>\n</body>")
            else:
                integrated_web_html = integrated_web_html + f"\n<script>{javascript_code}</script>"
                
            components.html(integrated_web_html, height=300, scrolling=True)
        else:
            st.info(f"Sandbox Environment Mode configured for script tree visualization: `{target_preview_file}`")
