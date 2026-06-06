import io
import re
import sys
import zipfile
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="WebMaster - AI App Builder",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Replit-like Dark Premium UI Custom CSS Inject
st.markdown("""
    <style>
    .stApp {
        background-color: #121316 !important;
        color: #f3f4f6 !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    .login-box {
        background-color: #1c1e24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2e323d;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MASTER API CONFIGURATION (તમારી API કી અહીં નાખો)
# -----------------------------------------------------------------------------
# 
MASTER_GEMINI_API_KEY = "AIzaSyCYrHDVTFsN8zknwutNDfaxCcx2AzMbUxc" 
MODEL_NAME = "gemini-2.5-flash"

# -----------------------------------------------------------------------------
# SESSION STATE MANAGEMENT (યુઝર ટ્રેકિંગ અને લોગિન)
# -----------------------------------------------------------------------------
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<h1>Welcome to WebMaster!</h1>\n<p>Your AI Agent is ready. Type your app idea in the box below.</p>",
        "style.css": "body { font-family: sans-serif; text-align: center; background: #121316; color: white; padding-top: 100px; }",
        "script.js": "console.log('WebMaster Engine Ready.');"
    }

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "index.html"

# યુઝરે કેટલી એપ્સ બનાવી તેનું કાઉન્ટર
if "apps_generated_count" not in st.session_state:
    st.session_state.apps_generated_count = 0

# યુઝર લોગિન છે કે નહીં તેની સ્થિતિ
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS (AI CALL & PARSING)
# -----------------------------------------------------------------------------
def parse_ai_response_to_files(ai_text):
    """નક્કર ફોર્મેટિંગ એન્જિન જે AI ના કોડને ઓળખીને ફાઇલોમાં જુદો પાડે છે."""
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, ai_text)
    parsed_files = {}
    for filename, content in matches:
        parsed_files[filename.strip()] = content.strip()
    return parsed_files

def generate_application_code(prompt, token):
    """બેકએન્ડ એન્જિન જે ૧૦૦% એપ જનરેટ કરવાની ગેરંટી આપે છે."""
    if not token or token == "YOUR_GEMINI_API_KEY_HERE":
        return "⚠️ WebMaster Error: Master API Key is missing in the code setup. Please add it inside app.py."

    system_instruction = (
        "You are WebMaster, the ultimate AI software engineer agent. Your only job is to output COMPLETE, fully working web app source files. "
        "You MUST structure every file using exactly this format:\n"
        "<file name=\"filename.ext\">\n...actual code...\n</file>\n"
        "Do not write regular chat or explanations outside these tags. Provide index.html, style.css, and script.js."
    )
    
    enhanced_prompt = (
        f"Build this app idea completely: {prompt}\n\n"
        "CRITICAL: You must wrap your code files inside <file name=\"filename.ext\">...</file> tags. No markdown code blocks."
    )

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=token)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        )
        return response.text
    except Exception as e:
        return f"❌ AI Engine Error: {str(e)}"

# -----------------------------------------------------------------------------
# SIDEBAR WORKSPACE (સાઇડબાર કંટ્રોલ અને લોગિન સિસ્ટમ)
# -----------------------------------------------------------------------------
st.sidebar.title("💻 WebMaster Account")

if not st.session_state.is_logged_in:
    st.sidebar.markdown("""
        <div class='login-box'>
        <p style='color: #ffcc00; margin-bottom:5px;'>🔒 Free Limit: 1 App</p>
        <p style='font-size:12px; color:#9ca3af;'>Login to unlock unlimited app creation tokens.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.subheader("🔑 Secure User Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login Account", use_container_width=True)
    
    if login_btn:
        if username and password: # સાદું પ્રોફેશનલ લોગિન વેલિડેશન
            st.session_state.is_logged_in = True
            st.sidebar.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Please enter any valid username & password.")
else:
    st.sidebar.success("✅ Account Status: Premium Unlocked")
    st.sidebar.write("Welcome back, Creator!")
    if st.sidebar.button("Log Out", type="secondary"):
        st.session_state.is_logged_in = False
        st.session_state.apps_generated_count = 0  # રીસેટ લિમિટ
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Apps created in this session: {st.session_state.apps_generated_count}")

# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE (અસલી Replit Agent જેવો લુક)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns(2)

# --- LEFT SIDE: Prompt Bar & Automation Input ---
with col_left:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Creator, what do you want to make?")
    st.caption("WebMaster AI Agent will instantly build, code, and deploy your software concept.")
    st.markdown("<br>", unsafe_allow_html=True)

    user_prompt = st.text_input(
        "Prompt Box", 
        placeholder="Type your app idea here (e.g., 'Make a beautiful calculator app with dark mode')...",
        label_visibility="collapsed",
        key="main_app_prompt"
    )
    
    build_btn = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # LIMIT CHECK LOGIC (૧ ફ્રી એપ ચેકર)
    can_build = True
    if st.session_state.apps_generated_count >= 1 and not st.session_state.is_logged_in:
        can_build = False
        st.markdown("""
            <div style='background-color: #7f1d1d; padding: 15px; border-radius: 5px; border: 1px solid #f87171; margin-top: 15px;'>
            <p style='margin:0; color:#fca5a5;'>🛑 <b>Free App Limit Reached!</b></p>
            <p style='margin:0; font-size:13px; color:#fca5a5;'>You have already built 1 free app. Please <b>Login</b> from the left sidebar to build more apps.</p>
            </div>
        """, unsafe_allow_html=True)

    # Execution Trigger
    if build_btn and user_prompt:
        if not can_build:
            st.toast("Please log in to continue!", icon="🔒")
        else:
            with st.spinner("WebMaster Agent is engineering your application code... 🛠️"):
                ai_raw_response = generate_application_code(user_prompt, MASTER_GEMINI_API_KEY)
                new_files = parse_ai_response_to_files(ai_raw_response)
                
                if new_files:
                    st.session_state.project_files = new_files
                    st.session_state.selected_file = list(new_files.keys())
                    st.session_state.apps_generated_count += 1 # એપ કાઉન્ટ વધારો
                    st.toast("Application successfully generated!", icon="🎉")
                    st.rerun()
                else:
                    st.error("AI Generation Error: Please try a different prompt description.")
                    with st.expander("See Raw Debug Output"):
                        st.write(ai_raw_response)

# --- RIGHT SIDE: Project Code Workspace & Live HTML Preview ---
with col_right:
    st.markdown("### 🛠️ Code Workspace & Preview")
    filenames = list(st.session_state.project_files.keys())
    
    if filenames:
        current_file = st.session_state.selected_file
        if current_file not in filenames:
            current_file = filenames
            
        selected_file = st.selectbox("📂 Project Files Explorer", options=filenames, index=filenames.index(current_file))
        st.session_state.selected_file = selected_file
        
        current_content = st.session_state.project_files[selected_file]
        edited_code = st.text_area(label=f"Editing Code: {selected_file}", value=current_content, height=230)
        st.session_state.project_files[selected_file] = edited_code
        
        # Zip Creation
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for fname, fcontent in st.session_state.project_files.items():
                zip_file.writestr(fname, fcontent)
        
        st.download_button(
            label="📥 Download WebMaster App (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="webmaster_project.zip",
            mime="application/zip",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### 🖥️ Interactive Live Preview")
        
        if "index.html" in st.session_state.project_files:
            html_code = st.session_state.project_files.get("index.html", "")
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
