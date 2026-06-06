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
    /* Main background color like Replit */
    .stApp {
        background-color: #121316 !important;
        color: #f3f4f6 !important;
    }
    /* Header customization */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        text-align: center;
    }
    /* Custom Styling for Cards and Quick Buttons */
    .suggestion-btn {
        background-color: #1c1e24;
        border: 1px solid #2e323d;
        color: #e5e7eb;
        padding: 10px 20px;
        border-radius: 20px;
        text-align: center;
        display: inline-block;
        margin: 5px;
        cursor: pointer;
        font-size: 14px;
    }
    .suggestion-btn:hover {
        background-color: #2e323d;
        border-color: #4b5563;
    }
    /* Center container helper */
    .center-text {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONFIGURATIONS (WebMaster Sidebar)
# -----------------------------------------------------------------------------
st.sidebar.title("💻 WebMaster Workspace")
st.sidebar.caption("Powered by Advanced AI Agent Engine")
st.sidebar.markdown("---")

api_provider = st.sidebar.selectbox(
    "Choose AI Engine Provider",
    ["Google Gemini", "Hugging Face"]
)

if api_provider == "Google Gemini":
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get a free key from Google AI Studio")
    model_name = "gemini-2.0-flash"
else:
    api_key = st.sidebar.text_input("Enter Hugging Face Token", type="password", help="Get a free token from HF settings")
    model_name = st.sidebar.selectbox(
        "Select HF Model", 
        ["Qwen/Qwen3.5-4B-Instruct", "meta-llama/Llama-3.3-70B-Instruct"]
    )

st.sidebar.markdown("---")
project_type = st.sidebar.selectbox(
    "Target Platform",
    ["Web App (HTML, CSS, JS)", "PC Desktop App (Python Tkinter)", "Mobile App Layout (Kivy/HTML5)"]
)

# Initialize Session States
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<h1>Hi, what do you want to make today?</h1>\n<p>Use the central prompt bar to instruct WebMaster AI Agent.</p>",
        "style.css": "body { font-family: sans-serif; text-align: center; background: #121316; color: white; padding-top: 100px; }",
        "script.js": "console.log('WebMaster Engine Ready.');"
    }

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "index.html"

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = ""

# -----------------------------------------------------------------------------
# 4. UTILITY FUNCTIONS
# -----------------------------------------------------------------------------
def parse_ai_response_to_files(ai_text):
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, ai_text)
    parsed_files = {}
    for filename, content in matches:
        parsed_files[filename.strip()] = content.strip()
    return parsed_files

def generate_application_code(prompt, provider, token, p_type):
    system_instruction = (
        "You are WebMaster, an elite automated AI software engineer agent like Replit Agent. Your task is to output complete, runnable code files "
        "for the requested application. You MUST structure your output using <file name=\"filename.ext\">...code...</file> tags. "
        "Make sure to output ALL required files. Do not give markdown explanation blocks outside the XML tags. "
        f"Target: {p_type}. Give complete, production-ready, beautifully designed pages. No placeholder comments."
    )
    enhanced_prompt = f"{prompt}\n\nWrap every file code inside <file name=\"filename.ext\">...code...</file> tags completely."

    if not token:
        return "⚠️ Please enter your API key/token in the sidebar to talk to the AI."

    try:
        if provider == "Google Gemini":
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=token)
            response = client.models.generate_content(
                model=model_name,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
            )
            return response.text
        elif provider == "Hugging Face":
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=token)
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": enhanced_prompt}
            ]
            response = client.chat.completions.create(model=model_name, messages=messages, max_tokens=3000, temperature=0.3)
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices.message.content
            return "❌ Unexpected response from Hugging Face API."
    except Exception as e:
        return f"❌ Error communicating with AI API:\n`{str(e)}`"

# -----------------------------------------------------------------------------
# 5. MAIN INTERFACE SPLIT (Replit Dashboard Look)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns()

# --- LEFT SIDE: Replit Central Input Console ---
with col_left:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Anchaudhari2025, what do you want to make?")
    st.caption("WebMaster AI Agent will instantly build, code, and deploy your idea.")
    
    # Quick Category Prompt Fillers
    st.markdown("<div class='center-text'>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🌐 Website"): 
            st.session_state.quick_prompt = "Create a modern portfolio website for a developer with dark mode"
            st.rerun()
    with c2:
        if st.button("📱 Mobile"): 
            st.session_state.quick_prompt = "Design a mobile-responsive habit tracker app dashboard layout"
            st.rerun()
    with c3:
        if st.button("🎨 Design"): 
            st.session_state.quick_prompt = "Build a beautiful landing page for an AI agency with glassmorphism UI"
            st.rerun()
    with c4:
        if st.button("📊 Slides"): 
            st.session_state.quick_prompt = "Create an interactive presentation slide viewer component in HTML"
            st.rerun()
    with c5:
        if st.button("📈 Data Vis"): 
            st.session_state.quick_prompt = "Build a financial budget tracker with live dashboard interactive charts"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Main Central Input Box
    user_prompt = st.text_input(
        "Make a launch video about...", 
        value=st.session_state.quick_prompt,
        placeholder="Type an app idea here (e.g., 'Make a classic snake game with scoreboard')...",
        key="main_prompt_input"
    )
    
    build_btn = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # Example Prompt Chips
    st.markdown("<p style='text-align:center;color:#6b7280;margin-top:15px;'>Try an example prompt 🔄</p>", unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        if st.button("Fitness app onboarding wireframe", use_container_width=True):
            st.session_state.quick_prompt = "Build a fitness app onboarding screen wireframe with beautiful step forms"
            st.rerun()
    with ex2:
        if st.button("B2B project management app", use_container_width=True):
            st.session_state.quick_prompt = "Create a full B2B project management Kanban board dashboard application"
            st.rerun()
    with ex3:
        if st.button("Product launch presentation", use_container_width=True):
            st.session_state.quick_prompt = "Make an interactive product launch presentation deck with sliding animations"
            st.rerun()

    # Execution Action Logic
    if build_btn and user_prompt:
        with st.spinner("WebMaster Agent is engineering your application code... 🛠️"):
            ai_raw_response = generate_application_code(user_prompt, api_provider, api_key, project_type)
            new_files = parse_ai_response_to_files(ai_raw_response)
            
            if new_files:
                st.session_state.project_files = new_files
                # પરફેક્ટ સોલ્યુશન: આખા લિસ્ટના બદલે ફક્ત પહેલી ફાઇલનું નામ (String) સેટ કર્યું
                st.session_state.selected_file = list(new_files.keys())
                st.toast("Application successfully generated!", icon="🎉")
                st.rerun()
            else:
                st.error("AI could not wrap files correctly. Raw output shown below:")
                st.code(ai_raw_response)

# --- RIGHT SIDE: Code Workspace & Interactive Live Preview ---
with col_right:
    st.markdown("### 🛠️ Code Workspace & Preview")
    filenames = list(st.session_state.project_files.keys())
    
    if filenames:
        # File selector dropdown
        selected_file = st.selectbox(
            "📂 Project Files Explorer", 
            options=filenames,
            index=filenames.index(st.session_state.selected_file) if st.session_state.selected_file in filenames else 0
        )
        st.session_state.selected_file = selected_file
        
        # Display
