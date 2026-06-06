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
        text-align: center;
    }
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
# Safely created columns with parameters fixed!
col_left, col_right = st.columns(2)

# --- LEFT SIDE: Replit Central Input Console ---
with col_left:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## Hi Anchaudhari2025, what do you want to make?")
    st.caption("WebMaster AI Agent will instantly build, code, and deploy your idea.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Main Central Input Box
    user_prompt = st.text_input(
        "Prompt Bar", 
        placeholder="Type an app idea here (e.g., 'Make a classic snake game with scoreboard')...",
        label_visibility="collapsed",
        key="main_prompt_input"
    )
    
    build_btn = st.button("🚀 Build & Run Application", use_container_width=True, type="primary")

    # Fixed Quick Idea helper text selection
    st.markdown("---")
    st.markdown("💡 **Quick Templates Reference:**")
    st.info("Copy & Paste these cool ideas into the prompt box above:\n\n"
            "1. `Build a beautiful portfolio website with dark-mode animation` \n"
            "2. `Create a B2B Kanban Board project management application` \n"
            "3. `Make a classic snake game with high-score tracking system` ")

    # Execution Action Logic
    if build_btn and user_prompt:
        with st.spinner("WebMaster Agent is engineering your application code... 🛠️"):
            ai_raw_response = generate_application_code(user_prompt, api_provider, api_key, project_type)
            new_files = parse_ai_response_to_files(ai_raw_response)
            
            if new_files:
                st.session_state.project_files = new_files
                if list(new_files.keys()):
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
        # Safely determine active index
        current_file = st.session_state.selected_file
        if current_file not in filenames:
            current_file = filenames
            
        selected_file = st.selectbox(
            "📂 Project Files Explorer", 
            options=filenames,
            index=filenames.index(current_file)
        )
        st.session_state.selected_file = selected_file
        
        # Display/Edit code
        current_content = st.session_state.project_files[selected_file]
        edited_code = st.text_area(label=f"Editing Code: {selected_file}", value=current_content, height=250)
        st.session_state.project_files[selected_file] = edited_code
        
        # Download Zip actions
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
        
        # Dynamic web simulation builder
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
                
            components.html(combined_html, height=400, scrolling=True)
        else:
            st.info("Live Preview is optimized for Web layout types.")
