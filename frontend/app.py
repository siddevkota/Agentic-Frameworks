"""
Streamlit Frontend for Email Agent
"""
import streamlit as st
import requests
from typing import Dict, Any

# Configure page
st.set_page_config(
    page_title="Email Agent Assistant",
    page_icon="📧",
    layout="wide"
)

# API Configuration
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .tool-badge {
        background-color: #E3F2FD;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📧 Email Agent Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered email processing with LangGraph</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    This email agent can help you with:
    
    - **Compose** professional emails
    - **Categorize** incoming emails
    - **Extract** action items
    - **Draft** replies
    
    Powered by LangGraph & OpenAI
    """)
    
    st.header("🔧 API Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    st.header("📚 Examples")
    st.caption("Try these prompts:")
    example_prompts = [
        "Compose an email to John about the meeting",
        "Categorize this: URGENT deadline tomorrow",
        "Extract action items from the email",
        "Draft a polite decline to the invitation"
    ]
    for prompt in example_prompts:
        if st.button(prompt, key=prompt):
            st.session_state.user_input = prompt

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Your Request")
    
    # Initialize session state
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    # Text input
    user_message = st.text_area(
        "What would you like help with?",
        value=st.session_state.user_input,
        height=150,
        placeholder="E.g., Compose a professional email to Sarah about the Q4 report...",
        key="text_area"
    )
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        process_button = st.button("🚀 Process", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.user_input = ""
            st.rerun()

with col2:
    st.subheader("🎯 Quick Actions")
    
    if st.button("📝 Compose Email", use_container_width=True):
        st.session_state.user_input = "Compose a professional email to the team about the upcoming project deadline."
        st.rerun()
    
    if st.button("🏷️ Categorize", use_container_width=True):
        st.session_state.user_input = "Categorize this email: 'URGENT: Please review the attached document ASAP.'"
        st.rerun()
    
    if st.button("✅ Action Items", use_container_width=True):
        st.session_state.user_input = "Extract action items from: 'Please complete the report by Friday and schedule a follow-up meeting.'"
        st.rerun()
    
    if st.button("💬 Draft Reply", use_container_width=True):
        st.session_state.user_input = "Draft a polite acknowledgment reply to a meeting invitation."
        st.rerun()

# Process request
if process_button and user_message:
    with st.spinner("🤔 Processing your request..."):
        try:
            # Call API
            response = requests.post(
                f"{API_URL}/process",
                json={"message": user_message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results
                st.success("✅ Request processed successfully!")
                
                # Response
                st.subheader("🤖 Agent Response")
                st.markdown(f"""
                <div style="background-color: #F5F5F5; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1E88E5;">
                    {result['response']}
                </div>
                """, unsafe_allow_html=True)
                
                # Tools used
                if result.get('tools_used'):
                    st.subheader("🔧 Tools Used")
                    tools_html = "".join([
                        f'<span class="tool-badge">{tool}</span>' 
                        for tool in result['tools_used']
                    ])
                    st.markdown(tools_html, unsafe_allow_html=True)
                
                # Metadata
                with st.expander("📊 Response Details"):
                    st.json(result)
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Please ensure the FastAPI server is running on port 8000.")
            st.code("python backend/main.py")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built with ❤️ using LangGraph, FastAPI & Streamlit
</div>
""", unsafe_allow_html=True)
