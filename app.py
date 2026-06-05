import io
import re
import sys
import time
import zipfile
import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page layout to wide
st.set_page_config(
    page_title="AI Multi-App Architect",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. SIDEBAR: Configs & Projects Settings
# -----------------------------------------------------------------------------
st.sidebar.title("🚀 App Architect Settings")
st.sidebar.markdown("Configure your engine to start building apps.")

# API Provider Selection
api_provider = st.sidebar.selectbox(
    "Choose AI Engine Provider",
    ["Google Gemini", "Hugging Face"]
)

# Dynamic Token Inputs depending on provider
if api_provider == "Google Gemini":
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get a free key from Google AI Studio")
    model_name = "gemini-2.0-flash"  # Auto-configured reliable model
else:
    api_key = st.sidebar.text_input("Enter Hugging Face Token", type="password", help="Get a free token from HF settings")
    model_name = st.sidebar.selectbox(
        "Select HF Model", 
        ["Qwen/Qwen3.5-4B-Instruct", "meta-llama/Llama-3.3-70B-Instruct"]
    )

st.sidebar.markdown("---")

# Project Settings
st.sidebar.subheader("Project Type")
project_type = st.sidebar.selectbox(
    "Target Platform",
    ["Web App (HTML, CSS, JS)", "PC Desktop App (Python Tkinter)", "Mobile App Layout (Kivy/HTML5)"]
)

st.sidebar.markdown("---")

# Initialize Session State Variables if they don't exist
if "project_files" not in st.session_state:
    st.session_state.project_files = {
        "index.html": "<h1>Welcome to App Architect!</h1>\n<p>Ask the AI on the left to build something amazing.</p>",
        "style.css": "body { font-family: sans-serif; text-align: center; background: #f0f2f6; padding: 50px; }",
        "script.js": "console.log('App successfully loaded!');"
    }

if "app_chat_history" not in st.session_state:
    st.session_state.app_chat_history = []

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "index.html"

# -----------------------------------------------------------------------------
# 2. PARSING UTILITIES
# -----------------------------------------------------------------------------
def parse_ai_response_to_files(ai_text):
    """Parses structured XML-like file tags from AI response."""
    pattern = r'<file\s+name="([^"]+)">([\s\S]*?)<\/file>'
    matches = re.findall(pattern, ai_text)
    
    parsed_files = {}
    for filename, content in matches:
        parsed_files[filename.strip()] = content.strip()
    
    return parsed_files

# -----------------------------------------------------------------------------
# 3. AI CALL UTILITIES WITH ACCURATE RATE-LIMIT RETRIES
# -----------------------------------------------------------------------------
def generate_application_code(prompt, provider, token, p_type):
    """Instructs LLM to write complete multi-file structures with built-in 429 error handling."""
    system_instruction = (
        "You are an elite automated software developer. Your task is to output complete, runnable code files "
        "for the user requested application. You MUST structure your output using <file name=\"filename.ext\">...code...</file> tags. "
        "Make sure to output ALL required files to run the application. Do not give markdown code blocks outside the XML tags. "
        f"The user wants a: {p_type}. Give complete, production-ready, beautifully designed pages. No placeholder comments.\n"
        "Example output:\n"
        "<file name=\"index.html\">\n<html>...</html>\n</file>\n"
        "<file name=\"style.css\">\nbody { ... }\n</file>"
    )

    enhanced_prompt = (
        f"{prompt}\n\nCRITICAL REQUIREMENT: Implement this completely. "
        "Wrap every single file code inside <file name=\"filename.ext\">...code...</file> tags. "
        "Do not leave any files out."
    )

    if not token:
        return "⚠️ Please enter your API key/token in the sidebar to talk to the AI."

    # Max retries configuration for Rate Limits
    max_retries = 3
    initial_delay = 4  # seconds

    for attempt in range(max_retries):
        try:
            if provider == "Google Gemini":
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=token)
                response = client.models.generate_content(
                    model=model_name,
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                    )
                )
                return response.text
                
            elif provider == "Hugging Face":
                from huggingface_hub import InferenceClient
                
                client = InferenceClient(api_key=token)
                messages = [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": enhanced_prompt}
                ]
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=3000,
                    temperature=0.3
                )
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    return response.choices.message.content
                return "❌ Unexpected response from Hugging Face API."
                
        except Exception as e:
            err_msg = str(e)
            # Check if the error is a 429 rate limit issue
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                if attempt < max_retries - 1:
                    # Informative sleep that increases dynamically
                    time.sleep(initial_delay * (attempt + 1))
                    continue
                else:
                    return (
                        "⚠️ **Gemini Free-Tier Limit Reached (429 Resource Exhausted)**\n\n"
                        "You have temporarily maxed out your free API quota. Please try one of the following:\n"
                        "1. Wait 10-15 seconds and try sending your request again.\n"
                        "2. Switch your provider to **Hugging Face** in the sidebar.\n"
                        "3. Set up a billing account on Google AI Studio to unlock higher tier limits."
                    )
            # Catch all other errors
            return f"❌ Error communicating with the AI API:\n`{err_msg}`"

# -----------------------------------------------------------------------------
# 4. CHAT INTERFACE & GENERATION CONTROL (LEFT COLUMN)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.header("💬 AI App Builder Studio")
    st.caption("Instruct the AI to create, redesign, or expand any software concept.")
    
    with st.expander("💡 App Ideas to Try"):
        st.markdown(
            "- **Scientific Calculator App** (Web or PC)\n"
            "- **Modern Pomodoro Timer App** with sounds\n"
            "- **Interactive Budget Expense Tracker** with charts\n"
            "- **Classic Snake Game** (Web App)"
        )
        
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.app_chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    if user_prompt := st.chat_input("Explain the application you want to build..."):
        with chat_container:
            with st.chat_message("user"):
                st.write(user_prompt)
        st.session_state.app_chat_history.append({"role": "user", "content": user_prompt})
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Engineering your application code... 🛠️ (Will auto-retry if rate limits are hit)"):
                    ai_raw_response = generate_application_code(user_prompt, api_provider, api_key, project_type)
                    new_files = parse_ai_response_to_files(ai_raw_response)
                    
                    if new_files:
                        st.session_state.project_files = new_files
                        st.session_state.selected_file = list(new_files.keys())
                        st.success(f"Successfully generated {len(new_files)} files!")
                        st.session_state.app_chat_history.append({
                            "role": "assistant", 
                            "content": f"I have successfully generated your application! Created files: {', '.join(new_files.keys())}"
                        })
                        st.rerun()
                    else:
                        st.write(ai_raw_response)
                        st.session_state.app_chat_history.append({"role": "assistant", "content": ai_raw_response})

# -----------------------------------------------------------------------------
# 5. MULTI-FILE WORKSPACE & PREVIEW SYSTEM (RIGHT COLUMN)
# -----------------------------------------------------------------------------
with col_right:
    st.header("🛠️ Code Workspace & Live Preview")
    filenames = list(st.session_state.project_files.keys())
    
    if filenames:
        active_index = 0
        if st.session_state.selected_file in filenames:
            active_index = filenames.index(st.session_state.selected_file)
            
        selected_file = st.selectbox(
            "📂 Active Project Files Explorer", 
            options=filenames,
            index=active_index,
            key="file_selector"
        )
        st.session_state.selected_file = selected_file
        
        current_content = st.session_state.project_files[selected_file]
        
        edited_code = st.text_area(
            label=f"Editing: {selected_file}",
            value=current_content,
            height=300,
            key=f"editor_{selected_file}"
        )
        st.session_state.project_files[selected_file] = edited_code
        
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for fname, fcontent in st.session_state.project_files.items():
                    zip_file.writestr(fname, fcontent)
            
            st.download_button(
                label="📥 Download App as ZIP",
                data=zip_buffer.getvalue(),
                file_name="generated_app_project.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            
        with w_col2:
            if st.button("🗑️ Reset Workspace", use_container_width=True):
                st.session_state.project_files = {
                    "index.html": "<h1>Welcome back!</h1>\n<p>Start a new app idea in the builder.</p>",
                    "style.css": "body { font-family: sans-serif; text-align: center; }",
                    "script.js": ""
                }
                st.session_state.selected_file = "index.html"
                st.rerun()

        st.markdown("---")
        st.subheader("🖥️ Interactive Live Preview")
        
        if "index.html" in st.session_state.project_files:
            html_code = st.session_state.project_files.get("index.html", "")
            css_code = st.session_state.project_files.get("style.css", "")
            js_code = st.session_state.project_files.get("script.js", "")
            
            combined_preview_html = html_code
            if "<head>" in combined_preview_html:
                combined_preview_html = combined_preview_html.replace("<head>", f"<head>\n<style>{css_code}</style>")
            else:
                combined_preview_html = f"<style>{css_code}</style>\n" + combined_preview_html
                
            if "</body>" in combined_preview_html:
                combined_preview_html = combined_preview_html.replace("</body>", f"<script>{js_code}</script>\n</body>")
            else:
                combined_preview_html = combined_preview_html + f"\n<script>{js_code}</script>"
                
            components.html(combined_preview_html, height=450, scrolling=True)
        else:
            st.info("Live Preview is available for Web Projects. For Desktop or Mobile layouts, inspect and download the code templates directly.")
    else:
        st.info("Let the AI generate code files to unlock the live workspace & compiler tools!")
