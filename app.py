import io
import re
import uuid
import zipfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration (Premium Replit Workspace Style)
st.set_page_config(
    page_title="WebMaster Pro - Ultimate Agent",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Hardcoded API Settings (Enter your active Gemini API Key here)
# -----------------------------------------------------------------------------
USER_GEMINI_KEY = "AIzaSyA9zukoNhfF419sKDFifc3wrV4DacfoyoY"
MODEL_ENGINE_NAME = "gemini-1.5-flash"  # Highly stable and 100% free model
# -----------------------------------------------------------------------------

# 3. Replit Dark Theme UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0c0d0e !important; color: #f3f4f6 !important; }
    h1, h2, h3, p, span, label { font-family: 'Inter', sans-serif !important; }
    .stTextArea textarea {
        background-color: #141619 !important;
        color: #ffffff !important;
        border: 1px solid #282a30 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus { border-color: #3e424b !important; box-shadow: none !important; }
    .login-container { background-color: #141619; padding: 20px; border-radius: 8px; border: 1px solid #22252a; margin-bottom: 20px; }
    .publish-box { background-color: #064e3b; color: #34d399; padding: 15px; border-radius: 6px; border: 1px solid #059669; margin-top: 15px; text-align: center; }
    .url-display { background-color: #1e1b4b; color: #818cf8; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 14px; margin-top: 10px; border: 1px solid #4338ca; word-break: break-all; }
    </style>
""", unsafe_allow_html=True)

# 4. Session State Management
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<div style='text-align:center; padding-top:40px;'><h1>Welcome to WebMaster Canvas</h1><p>Your workspace is ready. Use the left console to start generating live applications.</p></div>",
        "style.css": "body { font-family: sans-serif; background-color: #0c0d0e; color: white; text-align: center; }",
        "script.js": "console.log('WebMaster Live Preview Engine Active.');"
    }
if "selected_file" not in st.session_state: st.session_state.selected_file = "index.html"
if "generated_apps_tracker" not in st.session_state: st.session_state.generated_apps_tracker = 0
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "published_url" not in st.session_state: st.session_state.published_url = None

# 5. REST API Engine (Fully Optimized for Web, Mobile, and PC App Generation)
def build_application_backend(prompt, api_key):
    clean_key = str(api_key).strip()
    if not clean_key or clean_key == "YOUR_GEMINI_2_5_API_KEY_HERE":
        return "❌ WebMaster Configuration Notice: Please open app.py and enter your active Gemini API Key on line 22."
    
    full_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE_NAME}:generateContent?key={clean_key}"
    headers = {'Content-Type': 'application/json'}
    
    system_rules = (
        "You are WebMaster Pro, an elite software architect like Replit Agent. Your job is to build FULLY FUNCTIONAL, WORKING, INTERACTIVE applications, web apps, mobile apps, or tools based on user request. "
        "You must output ALL necessary frontend components (HTML, CSS, JavaScript) so it can run directly in a browser sandbox. "
        "You MUST wrap each file code inside XML format tags EXACTLY like this:\n"
        "<file name=\"index.html\">\n...fully working html structure with UI elements...\n</file>\n"
        "<file name=\"style.css\">\n...complete responsive modern CSS design...\n</file>\n"
        "<file name=\"script.js\">\n...interactive working functional logic Javascript code...\n</file>\n"
        "CRITICAL: Do not write explanations, markdown text, or descriptions outside the XML file tags. Only output the tags and code."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_rules}\n\nBuild Request: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(full_url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            candidate = res_json['candidates']
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                return candidate['content']['parts']['text']
        
        error_msg = res_json.get('error', {}).get('message', 'Unknown AI Engine response structure.')
        return f"❌ AI Engine Error: {error_msg}"
        
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# 6. Ultra Smart Code Extractor (Parser)
def parse_incoming_file_tree(response_text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, response_text)
    
    if not matches:
        pattern = r"<file\s+name='([^']+)'>([\s\S]*?)<\/file>"
        matches = re.findall(pattern, response_text)
        
    if matches:
        return {fname.strip(): content.strip() for fname, content in matches}
        
    # Markdown Fallback Filter
    files_dict = {}
    html_match = re.search(r'```html([\s\S]*?)```', response_text)
    css_match = re.search(r'```css([\s\S]*?)```', response_text)
    js_match = re.search(r'```javascript([\s\S]*?)```', response_text) or re.search(r'```js([\s\S]*?)```', response_text)
    
    if html_match: files_dict["index.html"] = html_match.group(1).strip()
    if css_match: files_dict["style.css"] = css_match.group(1).strip()
    if js_match: files_dict["script.js"] = js_match.group(1).strip()
    
    return files_dict

# 7. Main Layout Dashboard (All English Interface)
left_console, right_workspace = st.columns(2)

with left_console:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Creator, what do you want to make?")
    st.caption("WebMaster Pro Agent will write, evaluate, and assemble your full production build.")
    st.markdown("<br>", unsafe_allow_html=True)

    # FIXED: Perfectly structured text area with closed parenthesis
    user_prompt_input = st.text_area(
        "Prompt Input Element",
        placeholder="give here your mind thought",
        height=140,
        label_visibility="collapsed",
        key="central_replit_prompt"
    )
    
    trigger_build = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # 1 Free App Gate Limit Feature
    allow_compilation = True
    if st.session_state.generated_apps_tracker >= 1 and not st.session_state.is_logged_in:
        allow_compilation = False
        st.markdown("""
            <div style='background-color: #3b1414; padding: 15px; border-radius: 6px; border: 1px solid #ef4444; margin-top: 15px;'>
            <p style='margin:0; color:#fca5a5; font-weight:bold;'>🛑 Free Sandbox Limit Reached</p>
            <p style='margin:0; font-size:13px; color:#d1d5db;'>You have engineered 1 free application sandbox. Please <b>Login</b> on the sidebar account system to continue creating architectures.</p>
            </div>
        """, unsafe_allow_html=True)

    if trigger_build and user_prompt_input:
        if not allow_compilation:
            st.toast("Authorization token missing. Please sign in.", icon="🔒")
        else:
            with st.spinner("WebMaster AI Agent is building live application modules... 🛠️"):
                raw_response = build_application_backend(user_prompt_input, USER_GEMINI_KEY)
                extracted_files = parse_incoming_file_tree(raw_response)
                
                if extracted_files:
                    st.session_state.project_files = extracted_files
                    st.session_state.
