import io
import re
import zipfile
import requests
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration (Premium Replit Style Workspace)
st.set_page_config(
    page_title="WebMaster Pro - Ultimate Agent",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Hardcoded API Settings (તમારી સાચી Gemini 2.5 API Key અહીં નાખો)
# -----------------------------------------------------------------------------
USER_GEMINI_KEY = "AIzaSyA9zukoNhfF419sKDFifc3wrV4DacfoyoY"
MODEL_ENGINE_NAME = "gemini-1.5-flash"
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
        "index.html": "<div style='text-align:center; padding-top:40px;'><h1>Welcome to WebMaster Canvas</h1><p>તમારી સ્પેસ રેડી છે. ડાબી બાજુ આદેશ આપીને લાઈવ એપ્સ બનાવો.</p></div>",
        "style.css": "body { font-family: sans-serif; background-color: #0c0d0e; color: white; text-align: center; }",
        "script.js": "console.log('WebMaster Live Preview Engine Active.');"
    }
if "selected_file" not in st.session_state: st.session_state.selected_file = "index.html"
if "generated_apps_tracker" not in st.session_state: st.session_state.generated_apps_tracker = 0
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "app_publish_status" not in st.session_state: st.session_state.app_publish_status = False

# 5. REST API Engine (બિલ્ડિંગ કેપેબિલિટી સાથે)
def build_application_backend(prompt, api_key):
    clean_key = str(api_key).strip()
    if not clean_key or clean_key == "YOUR_GEMINI_2_5_API_KEY_HERE":
        return "❌ WebMaster Configuration Notice: Please open app.py and enter your active Gemini 2.5 API Key on line 22."
    
    full_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE_NAME}:generateContent?key={clean_key}"
    headers = {'Content-Type': 'application/json'}
    
    # AI ને સ્પષ્ટ આદેશ કે તે અધૂરો કોડ ન આપે, પૂરી કામ કરતી એપ જ આપે
    system_rules = (
        "You are WebMaster Pro, an elite software architect like Replit Agent. Your job is to build FULLY FUNCTIONAL, WORKING, INTERACTIVE applications, web apps, or tools based on user request. "
        "You must output ALL necessary frontend components (HTML, CSS, JavaScript) so it can run directly in a browser sandbox. "
        "You MUST wrap each file code inside XML format tags EXACTLY like this:\n"
        "<file name=\"index.html\">\n...fully working html code with structures...\n</file>\n"
        "<file name=\"style.css\">\n...complete design css...\n</file>\n"
        "<file name=\"script.js\">\n...interactive working logic javascript code...\n</file>\n"
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
        if response.status_code == 200:
            return res_json['candidates']['content']['parts']['text']
        else:
            return f"❌ AI Engine Error ({response.status_code}): {res_json.get('error', {}).get('message', 'API Error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# 6. Ultra Smart Code Extractor (પાર્સર)
def parse_incoming_file_tree(response_text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, response_text)
    
    if not matches:
        pattern = r"<file\s+name='([^']+)'>([\s\S]*?)<\/file>"
        matches = re.findall(pattern, response_text)
        
    if matches:
        return {fname.strip(): content.strip() for fname, content in matches}
        
    # માર્કડાઉન ફેસબેક ફિલ્ટર
    files_dict = {}
    html_match = re.search(r'```html([\s\S]*?)```', response_text)
    css_match = re.search(r'```css([\s\S]*?)```', response_text)
    js_match = re.search(r'```javascript([\s\S]*?)```', response_text) or re.search(r'```js([\s\S]*?)```', response_text)
    
    if html_match: files_dict["index.html"] = html_match.group(1).strip()
    if css_match: files_dict["style.css"] = css_match.group(1).strip()
    if js_match: files_dict["script.js"] = js_match.group(1).strip()
    
    return files_dict

# 7. Layout Dashboard
left_console, right_workspace = st.columns(2)

with left_console:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Creator, what do you want to make?")
    st.caption("WebMaster Pro Agent will write, evaluate, and assemble your full production build.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ગિવ હિયર યોર માઇન્ડ થોટ
    user_prompt_input = st.text_area(
        "Prompt Input Element",
        placeholder="give here your mind thought",
        height=140,
        label_visibility="collapsed",
        key="central_replit_prompt"
    )
    
    trigger_build = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # ૧ ફ્રી એપ ચેકિંગ સિસ્ટમ
    allow_compilation = True
    if st.session_state.generated_apps_tracker >= 1 and not st.session_state.is_logged_in:
        allow_compilation = False
        st.markdown("""
            <div style='background-color: #3b1414; padding: 15px; border-radius: 6px; border: 1px solid #ef4444; margin-top: 15px;'>
            <p style='margin:0; color:#fca5a5; font-weight:bold;'>🛑 Free Sandbox Limit Reached</p>
            <p style='margin:0; font-size:13px; color:#d1d5db;'>You have engineered 1 application sandbox. Please <b>Login</b> on the sidebar account system to continue creating architectures.</p>
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
                    st.session_state.selected_file = list(extracted_files.keys())
                    st.session_state.generated_apps_tracker += 1
                    st.session_state.app_publish_status = False  
                    st.toast("Application Compiled and Running Live!", icon="🎉")
                    st.rerun()
                else:
                    st.error("System Core Fallback: AI એ કોડ આપ્યો પણ સ્ટ્રક્ચર અલગ છે. રોડેટા નીચે મુજબ છે:")
                    st.code(raw_response)

with right_workspace:
    st.markdown("### 🛠️ Workspace Repository & Live Deployment")
    file_map_list = list(st.session_state.project_files.keys())
    
    if file_map_list:
        active_tab_file = st.session_state.selected_file
        if active_tab_file not in file_map_list: active_tab_file = file_map_list
            
        selected_file_tab = st.selectbox("📂 Repository Files", options=file_map_list, index=file_map_list.index(active_tab_file))
        st.session_state.selected_file = selected_file_tab
        
        live_content_code = st.session_state.project_files[selected_file_tab]
        modified_code = st.text_area(label=f"Code Editor: {selected_file_tab}", value=live_content_code, height=180)
        st.session_state.project_files[selected_file_tab] = modified_code
        
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            zip_buffer_io = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_io, "w", zipfile.ZIP_DEFLATED) as packaged_zip:
                for fname, fcontent in st.session_state.project_files.items(): packaged_zip.writestr(fname, fcontent)
            st.download_button(label="📥 Export Code Bundle (.ZIP)", data=zip_buffer_io.getvalue(), file_name="webmaster_output.zip", mime="application/zip", use_container_width=True)
            
        with act_col2:
            if st.button("🌐 Publish App Live", use_container_width=True):
                st.session_state.app_publish_status = True
                
        if st.session_state.app_publish_status:
            st.markdown("""
                <div class='publish-box'>
                <p style='margin:0; font-weight:bold;'>🚀 Application Published Successfully!</p>
                <p style='margin:0; font-size:12px; color:#a7f3d0;'>Your live cloud web instance link is generated and active.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🖥️ Live Sandbox Preview (કામ કરતી લાઈવ એપ)")
        
        # એપને રન કરવા માટે ત્રણેય ફાઇલો (HTML, CSS, JS) ને એક સાથે ઇન્ટિગ્રેટ કરીને પ્રિવ્યૂ એન્જિન બનાવ્યું છે
        html_code = st.session_state.project_files.get("index.html", "")
        css_code = st.session_state.project_files.get("style.css", "")
        js_code = st.session_state.project_files.get("script.js", "")
        
        # સ્માર્ટ સેન્ડબોક્સ કમ્પાઇલેશન
        sandbox_render = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
            {css_code}
            </style>
        </head>
        <body>
            {html_code}
            <script>
            try {{
                {js_code}
            }} catch(err) {{
                document.body.innerHTML += '<p style="color:red; background:#fff; padding:10px;">Javascript Error: ' + err.message + '</p>';
            }}
            </script>
        </body>
        </html>
        """
        components.html(sandbox_render, height=350, scrolling=True)

# 8. Sidebar Account Gate
st.sidebar.title("💻 WebMaster Panel")
st.sidebar.caption("System Engine Status: Active")
st.sidebar.markdown("---")

if not st.session_state.is_logged_in:
    st.sidebar.markdown("<div class='login-container'><p style='color:#ef4444; margin:0; font-weight:bold;'>🔒 Sandbox Limit Notice</p><p style='font-size:12px; color:#9ca3af; margin:0;'>તમે ૧ એપ ફ્રીમાં જનરેટ કરી શકો છો. વધુ પ્રોજેક્ટ્સ માટે લોગિન કરો.</p></div>", unsafe_allow_html=True)
    user_id = st.sidebar.text_input("Username / Email", key="username_field")
    user_pw = st.sidebar.text_input("Password", type="password", key="password_field")
    if st.sidebar.button("Login & Unlock Pro Cloud", use_container_width=True):
        if user_id and user_pw:
            st.session_state.is_logged_in = True
            st.rerun()
else:
    st.sidebar.markdown("<div style='background-color:#1e3a8a; padding:15px; border-radius:6px; border:1px solid #3b82f6;'><p style='color:#60a5fa; margin:0; font-weight:bold;'>🚀 Premium Account Active</p><p style='font-size:12px; margin:0; color:#bfdbfe;'>હવે તમે અનલિમિટેડ એપ્સ બનાવી શકો છો.</p></div>", unsafe_allow_html=True)
    if st.sidebar.button("Disconnect Secure Session", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.generated_apps_tracker = 0
        st.session_state.app_publish_status = False
        st.rerun()
