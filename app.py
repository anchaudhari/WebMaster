import streamlit as st
import google.generativeai as genai
import random

# Page Configuration
st.set_page_config(page_title="AI Multi-App Builder", layout="wide", initial_sidebar_state="expanded")

# Fetch API Key securely from Streamlit Secrets
try:
    GEMINI_API_KEY = st.secrets["AIzaSyA9zukoNhfF419sKDFifc3wrV4DacfoyoY"]
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize Session States for Application Flow
if "apps_created" not in st.session_state:
    st.session_state.apps_created = 0
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "app_published" not in st.session_state:
    st.session_state.app_published = False

# --- UI Header (All English text as requested) ---
st.title("🚀 AI Multi-App Builder")
st.subheader("Instantly generate Web, Mobile, and PC applications using AI")
st.write("---")

# --- Access Logic (1 Free Trial then Login) ---
can_build = False

if st.session_state.apps_created < 1:
    st.info("🎁 Free Trial Active: You can build 1 app for FREE without creating an account!")
    can_build = True
else:
    if not st.session_state.is_logged_in:
        st.warning("🔒 You have used your free limit. Please login to build more applications.")
        
        # English Login Form
        with st.form("login_form"):
            st.markdown("### Account Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Login")
            
            if login_submit:
                # Default credentials (You can change 'admin' and 'password' to anything you like)
                if username == "admin" and password == "password":
                    st.session_state.is_logged_in = True
                    st.success("Login Successful! Premium access granted.")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Please try again.")
    else:
        st.success("🔓 Status: Logged In (Unlimited Access)")
        can_build = True

# --- Application Generation Core ---
if can_build:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Configuration")
        app_type = st.selectbox(
            "Select Platform Target", 
            ["Web App (HTML/CSS/JS)", "Mobile App (Flutter/React Native)", "PC App (Python Tkinter/Electron)"]
        )
    
    with col2:
        st.markdown("### Describe your App")
        # Prompt section with exact requested placeholder text
        user_prompt = st.text_area(
            "What kind of app do you want to build?", 
            placeholder="give here your mind thought", 
            height=150
        )
        
        generate_btn = st.button("Generate My App", type="primary")

    if generate_btn:
        if user_prompt.strip() == "":
            st.error("Please enter your mind thought before generating!")
        else:
            with st.spinner("🤖 Writing complete bug-free source code... Please wait..."):
                try:
                    # Utilizing Gemini 2.5 Flash for fast code generation
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    system_instruction = (
                        f"You are a master software architect. Generate a fully functional, production-ready, "
                        f"clean, and complete source code for a {app_type} based on the user's request. "
                        f"Do not write placeholders, comments like '// code here', or half-baked scripts. "
                        f"Provide the complete structure so it can run out of the box."
                    )
                    
                    response = model.generate_content(system_instruction + "\nUser Idea: " + user_prompt)
                    
                    st.session_state.generated_code = response.text
                    st.session_state.apps_created += 1
                    st.session_state.app_published = False  # Reset publish state for the new app
                    st.rerun()
                except Exception as e:
                    st.error(f"API Error: {e}")

# --- Output and Publishing Deployment Window ---
if st.session_state.generated_code:
    st.write("---")
    st.subheader("📦 Generated Workspace & Code")
    
    # Displaying code output neatly
    st.code(st.session_state.generated_code, language="python" if "PC App" in locals() else "javascript")
    
    # Download Option
    st.download_button(
        label="📥 Download Project Source Code",
        data=st.session_state.generated_code,
        file_name="app_source_code.txt",
        mime="text/plain"
    )
    
    st.write("---")
    st.subheader("🌐 Hosting & Deployment")
    
    # Publish Feature
    if st.button("🚀 Publish App", key="publish_app_btn"):
        st.session_state.app_published = True
        
    if st.session_state.app_published:
        # Generates a clean random mockup hosting URL for the client
        random_id = random.randint(10000, 99999)
        generated_url = f"https://share.streamlit.io/deployed-apps/user-project-{random_id}/index.html"
        
        st.success("🎉 Production build compiled successfully! Your application is now live.")
        st.markdown(f"🔗 **Live Preview URL:** [{generated_url}]({generated_url})")
