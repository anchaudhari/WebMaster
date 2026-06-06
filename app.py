import io
import re
import zipfile
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai  # Method updated to fix 401 Error

# 1. Page Configuration
st.set_page_config(
    page_title="WebMaster Pro - Fix 401 Edition",
    page_icon="💻",
    layout="wide"
)

# 2. UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0e1013 !important; color: #f3f4f6 !important; }
    .login-box { background-color: #161a22; padding: 20px; border-radius: 10px; border: 1px solid #21263d; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
if "project_files" not in st.session_state:
    st.session_state.project_files = {"index.html": "<h1>Ready to Build</h1>", "style.css": "body{background:#0e1013; color:white;}", "script.js": ""}
if "apps_generated_count" not in st.session_state:
    st.session_state.apps_generated_count = 0
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# -----------------------------------------------------------------------------
# FIXED ENGINE (Fixes 401 Unauthenticated Error)
# -----------------------------------------------------------------------------
def generate_complex_application(prompt, api_key, model_choice):
    if not api_key:
        return "⚠️ Please enter API Key in sidebar."
    
    try:
        # Correct way to configure API key to avoid 401 error
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_choice)
        
        system_instruction = "Output files in <file name='filename'>code</file> format only."
        full_prompt = f"{system_instruction}\n\nBuild this app: {prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

def parse_files(text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, text)
    return {fname.strip(): content.strip() for fname, content in matches}

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("💻 Settings")
user_api = st.sidebar.text_input("Gemini API Key", type="password")
model_engine = st.sidebar.selectbox("Select Model", ["gemini-1.5-flash", "gemini-1.5-pro"])

st.sidebar.markdown("---")
if not st.session_state.is_logged_in:
    st.sidebar.info("🔒 1 Free App Available")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        st.session_state.is_logged_in = True
        st.rerun()
else:
    st.sidebar.success("✅ Pro Unlocked")
    if st.sidebar.button("Logout"):
        st.session_state.is_logged_in = False
        st.rerun()

# -----------------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("Build Classplus Clone")
    prompt = st.text_area("What should the app do?", height=150)
    
    # Logic for Free Limit
    if st.session_state.apps_generated_count >= 1 and not st.session_state.is_logged_in:
        st.warning("Limit reached. Please Login.")
    else:
        if st.button("🚀 Build App"):
            raw = generate_complex_application(prompt, user_api, model_engine)
            files = parse_files(raw)
            if files:
                st.session_state.project_files = files
                st.session_state.apps_generated_count += 1
                st.rerun()
            else:
                st.code(raw)

with col2:
    st.header("Preview & Code")
    f_names = list(st.session_state.project_files.keys())
    sel = st.selectbox("Files", f_names)
    st.code(st.session_state.project_files[sel])
    
    # Download ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for fn, fc in st.session_state.project_files.items():
            z.writestr(fn, fc)
    st.download_button("📥 Download ZIP", buf.getvalue(), "app.zip")
