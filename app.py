import io
import re
import zipfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="WebMaster Pro - Ultimate Agent",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Hardcoded API Settings (તમારી સાચી Gemini API Key અહીં નાખો)
# -----------------------------------------------------------------------------
USER_GEMINI_KEY = " AQ.Ab8RN6I217zugbkJs493Ek-oFQcMaGrCyfUD3YFjZOHv5QnyAA"
MODEL_ENGINE_NAME = "gemini-1.5-flash"  # ફ્રી અને સ્ટેબલ મોડેલ
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
    </style>
""", unsafe_allow_html=True)

# 4. Session State Management
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<div style='text-align:center;'><h1>Welcome to WebMaster</h1><p>Your workspace is live. Use the left console to start generating apps.</p></div>",
        "style.css": "body { font-family: sans-serif; background-color: #0c0d0e; color: white; padding-top: 50px; }",
        "script.js": "console.log('WebMaster Ultimate Workspace loaded.');"
    }
if "selected_file" not in st.session_state: st.session_state.selected_file = "index.html"
if "generated_apps_tracker" not in st.session_state: st.session_state.generated_apps_tracker = 0
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "app_publish_status" not in st.session_state: st.session_state.app_publish_status = False

# 5. Dynamic REST API Engine (મોડેલ મુજબ ઓટોમેટિક URL ચેન્જ થશે)
def build_application_backend(prompt, api_key):
    clean_key = str(api_key).strip()
    clean_model = str(MODEL_ENGINE_NAME).strip()
    
    if not clean_key or clean_key == "YOUR_GEMINI_API_KEY_HERE":
        return "❌ WebMaster Configuration Notice: Please open app.py and enter your active Gemini API Key on line 21."
    
    # FIXED: હવે URL તમે ઉપર સેટ કરેલા મોડેલ (gemini-1.5-flash) મુજબ ડાયનેમિકલી બનશે
    full_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={clean_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    system_rules = (
        "You are WebMaster Pro, an elite software architect like Replit Agent. Build a fully functional system. "
        "You MUST output ALL code inside XML format tags EXACTLY like this:\n"
        "<file name=\"index.html\">\n...code...\n</file>\n"
        "<file name=\"style.css\">\n...code...\n</file>\n"
        "<file name=\"script.js\">\n...code...\n</file>\n"
        "Produce fully operational code. Do not write regular markdown explanations outside the tags."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_rules}\n\nBuild Request: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(full_url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates']['content']['parts']['text']
        else:
            error_msg = res_json.get('error', {}).get('message', 'Unknown API Error')
            return f"❌ AI Engine Error ({response.status_code}): {error_msg}\nતમારી API કી અને મોડેલનું નામ ચેક કરો."
    except Exception as e:
        return f"❌ HTTP Connection Error: {str(e)}"

# 6. Advanced Smart Parser
def parse_incoming_file_tree(response_text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, response_text)
    
    if not matches:
        pattern = r"<file\s+name='([^']+)'>([\s\S]*?)<\/file>"
        matches = re.findall(pattern, response_text)
        
    if not matches:
        files_dict = {}
        html_match = re.search(r'```html([\s\S]*?)```', response_text)
        css_match = re.search(r'```css([\s\S]*?)```', response_text)
        js_match = re.search(r'```javascript([\s\S]*?)```', response_text) or re.search(r'```js([\s\S]*?)```', response_text)
        
        if html_match: files_dict["index.html"] = html_match.group(1).strip()
        if css_match: files_dict["style.css"] = css_match.group(1).strip()
        if js_match: files_dict["script.js"] = js_match.group(1).strip()
        
        if files_dict:
            return files_dict
            
    return {fname.strip(): content.strip() for fname, content in matches} if matches else {}

# 7. Main Split UI Dashboard Layout
left_console, right_workspace = st.columns(2)

with left_console:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Creator, what do you want to make?")
    st.caption("WebMaster Pro Agent will write, evaluate, and assemble your full production build.")
    st.markdown("<br>", unsafe_allow_html=True)

    user_prompt_input = st.text_area(
        "Prompt Input Element",
        placeholder="give here your mind thought",
        height=140,
        label_visibility="collapsed",
        key="central_replit_prompt"
    )
    
    trigger_build = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    allow_compilation = True
    if st.session_state.generated_apps_tracker >= 1 and not st.session_state.is_logged_in:
        allow_compilation = False
