import io
import re
import sys
import zipfile
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="WebMaster Pro - LMS & App Builder",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Replit-like Ultra Dark CSS Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1013 !important;
        color: #f3f4f6 !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    .login-box {
        background-color: #161a22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #21263d;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MASTER API CONFIGURATION (તમારી સાચી API કી અહીં સેટ કરો)
# -----------------------------------------------------------------------------
# કોડની અંદર કી લખવાની જગ્યાએ આ સેફ લાઇન મૂકો
MY_GEMINI_KEY = "AQ.Ab8RN6IlzlzvRHHAiTILGbA_XG0JkbCSGLO54Ctafhh77mz0AA"
MODEL_NAME = "gemini-2.5-flash"  

# -----------------------------------------------------------------------------
# SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<h1>Welcome to WebMaster Pro!</h1>\n<p>Enter your massive app idea like 'Classplus Educational Platform' to begin.</p>",
        "style.css": "body { font-family: sans-serif; text-align: center; background: #0e1013; color: white; padding-top: 100px; }",
        "script.js": "console.log('WebMaster Core Engine Loaded Successfully.');"
    }

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "index.html"

if "apps_generated_count" not in st.session_state:
    st.session_state.apps_generated_count = 0

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# -----------------------------------------------------------------------------
# ADVANCED MULTI-FILE PARSING ENGINE
# -----------------------------------------------------------------------------
def parse_ai_response_to_files(ai_text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, ai_text)
    parsed_files = {}
    for filename, content in matches:
        parsed_files[filename.strip()] = content.strip()
    return parsed_files

def generate_complex_application(prompt, token):
    if not token or token == "YOUR_GEMINI_API_KEY_HERE":
        return "⚠️ WebMaster Error: Please hardcode your valid Gemini API Key inside app.py line 34."

    system_instruction = (
        "You are WebMaster Pro, a senior full-stack software architect agent specializing in complex platforms like Classplus, E-commerce, and SaaS. "
        "Your goal is to build comprehensive, working applications with multiple modular code files. "
        "You must structure every file completely and cleanly inside XML tags like this:\n"
        "<file name=\"filename.ext\">\n...code...\n</file>\n"
        "For complex learning systems like Classplus, output multiple files if needed (e.g., dashboard.html, store.html, quiz.html, script.js, style.css) "
        "so that the user gets a full architectural blueprint. Do not output conversational text or general markdown blocks outside the XML file tags."
    )
    
    enhanced_prompt = (
        f"Design and build this system completely: {prompt}\n\n"
        "CRITICAL ARCHITECTURE REQUIREMENT:\n"
        "Generate all required interactive full-stack interface files. "
        "Every single file must be enclosed within <file name=\"filename.ext\">...source code...</file> tags. No lazy truncation or placeholders."
    )

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=token)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"❌ System Engine Error: {str(e)}"

# -----------------------------------------------------------------------------
# SIDEBAR CONTROL
# -----------------------------------------------------------------------------
st.sidebar.title("💻 WebMaster Account")

if not st.session_state.is_logged_in:
    st.sidebar.markdown("""
        <div class='login-box'>
        <p style='color: #ff4b4b; margin-bottom:5px;'>🔒 Anonymous Mode Limit: 1 App</p>
        <p style='font-size:12px; color:#9ca3af;'>To build huge architectures like Classplus, login to unlock infinite file generations.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.subheader("🔑 Access Portal")
    username = st.sidebar.text_input("Username", key="user_login_id")
    password = st.sidebar.text_input("Password", type="password", key="user_login_pass")
    login_btn = st.sidebar.button("Login & Unlock Pro Engine", use_container_width=True)
    
    if login_btn:
        if username and password:
            st.session_state.is_logged_in = True
            st.sidebar.success("Pro Account Activated!")
            st.rerun()
        else:
            st.sidebar.error("Please provide both credentials.")
else:
    st.sidebar.success("🚀 WebMaster Pro Status: Active")
    st.sidebar.write("Unlimited Development Pipeline Unlocked.")
    if st.sidebar.button("Disconnect Session", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.apps_generated_count = 0
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"🔧 Total Builds Managed: {st.session_state.apps_generated_count}")

# -----------------------------------------------------------------------------
# MAIN REPLIT-STYLE DASHBOARD INTERFACE
# -----------------------------------------------------------------------------
col_left, col_right = st.columns(2)

# --- LEFT PANEL: Smart Prompt & Code Generation ---
with col_left:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## WebMaster Pro Architecture Studio")
    st.caption("Enter any high-end application request. The engine generates full code modules.")
    st.markdown("<br>", unsafe_allow_html=True)

    user_prompt = st.text_area(
        "Application Blueprint Input", 
        placeholder="Describe your enterprise idea (e.g., 'Build a complete Classplus LMS platform with a clean dashboard, course store module, student lecture viewer tab, and interactive quiz player')",
        height=150,
        label_visibility="collapsed",
        key="pro_app_prompt"
    )
    
    build_btn = st.button("🚀 Execute Architecture Generation", use_container_width=True, type="primary")

    # Limit guard logic
    can_build = True
    if st.session_state.apps_generated_count >= 1 and not st.session_state.is_logged_in:
        can_build = False
        st.markdown("""
            <div style='background-color: #3b1414; padding: 15px; border-radius: 8px; border: 1px solid #ef4444; margin-top: 15px;'>
            <p style='margin:0; color:#fca5a5;'>🛑 <b>Free Compilation Limit Enforced</b></p>
            <p style='margin:0; font-size:13px; color:#d1d5db;'>You have created 1 free software workspace. Please <b>Login</b> via the left side portal to generate advanced multi-module apps.</p>
            </div>
        """, unsafe_allow_html=True)

    if build_btn and user_prompt:
        if not can_build:
            st.toast("Authentication required for additional builds.", icon="🔒")
        else:
            with st.spinner("WebMaster AI Agent is industrializing your source code tree... 🛠️"):
                ai_raw_response = generate_complex_application(user_prompt, MASTER_GEMINI_API_KEY)
                new_files = parse_ai_response_to_files(ai_raw_response)
                
                if new_files:
                    st.session_state.project_files = new_files
                    st.session_state.selected_file = list(new_files.keys())
                    st.session_state.apps_generated_count += 1
                    st.toast("Code workspace refreshed with new modules!", icon="🎉")
                    st.rerun()
                else:
                    st.error("Engine Parsing Notification: Highly complex logic requested. Raw system output fallback activated below:")
                    with st.expander("Inspect Raw Response Tree"):
                        st.code(ai_raw_response)

# --- RIGHT PANEL: Professional Multi-File Workspace Explorer ---
with col_right:
    st.markdown("### 🛠️ Code Workspace & Preview")
    filenames = list(st.session_state.project_files.keys())
    
    if filenames:
        current_file = st.session_state.selected_file
        if current_file not in filenames:
            current_file = filenames
            
        selected_file = st.selectbox("📂 Active Project Repository Explorer", options=filenames, index=filenames.index(current_file))
        st.session_state.selected_file = selected_file
        
        current_content = st.session_state.project_files[selected_file]
        edited_code = st.text_area(label=f"Code Editor: {selected_file}", value=current_content, height=250)
        st.session_state.project_files[selected_file] = edited_code
        
        # Build comprehensive export zip package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for fname, fcontent in st.session_state.project_files.items():
                zip_file.writestr(fname, fcontent)
        
        st.download_button(
            label="📥 Export Full App Project Source Bundle (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="webmaster_pro_package.zip",
            mime="application/zip",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### 🖥️ Real-time Component Sandbox Preview")
        
        # Automatic environment stitching for main viewer files
        active_preview_file = "index.html" if "index.html" in st.session_state.project_files else filenames
        
        if active_preview_file.endswith(".html"):
            html_code = st.session_state.project_files.get(active_preview_file, "")
            css_code = st.session_state.project_files.get("style.css", "")
            js_code = st.session_state.project_files.get("script.js", "")
            
            combined_html = html_code
            if "<head>" in combined_html:
                combined_html = combined_html.replace("<head>", f"<head>\n<style>{css_code}</style>")
            else:
                combined_html = f"<style>{css_code}</style>\n" + combined_html
                
            if "</body>" in combined_html:
                combined_html = combined_html.replace("</body>", f"<script>{js_code}</script>\n</body>")
            else:
                combined_html = combined_html + f"\n<script>{js_code}</script>"
                
            components.html(combined_html, height=350, scrolling=True)
        else:
            st.info(f"Sandbox Preview optimized for markup files. Currently exploring raw backend script layout: `{active_preview_file}`")
