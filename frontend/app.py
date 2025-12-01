"""
Streamlit Frontend for Research Assistant
Real web search and information synthesis
"""
import streamlit as st
import requests
from typing import Dict, Any, List
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
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
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .tool-badge {
        background-color: #E3F2FD;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
        color: #1565C0;
        border: 1px solid #90CAF9;
    }
    .response-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .status-connected {
        color: #2e7d32;
        font-weight: bold;
    }
    .status-disconnected {
        color: #c62828;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .agent-message {
        background-color: #F1F8E9;
        border-left: 4px solid #7CB342;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Header
st.markdown('<h1 class="main-header">🔍 AI Research Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real Web Search • Information Analysis • Powered by LangGraph</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🎯 Capabilities")
    
    # Feature cards
    st.markdown("""
    <div class="feature-card">
        <h4>🌐 Web Search</h4>
        <p>Real-time DuckDuckGo search for current information</p>
    </div>
    <div class="feature-card">
        <h4>📄 Content Extraction</h4>
        <p>Fetch and analyze content from specific URLs</p>
    </div>
    <div class="feature-card">
        <h4>🧠 Information Analysis</h4>
        <p>Synthesize findings and identify key insights</p>
    </div>
    <div class="feature-card">
        <h4>📊 Report Generation</h4>
        <p>Create structured reports with sources</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.header("🔧 System Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.markdown('<p class="status-connected">✅ Backend Online</p>', unsafe_allow_html=True)
            st.caption(f"API: {API_URL}")
        else:
            st.markdown('<p class="status-disconnected">⚠️ Backend Issues</p>', unsafe_allow_html=True)
    except:
        st.markdown('<p class="status-disconnected">❌ Backend Offline</p>', unsafe_allow_html=True)
        st.error("Start backend: `python backend/main.py`")
    
    # Statistics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{st.session_state.request_count}</h3>
            <p>Requests</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(st.session_state.conversation_history)}</h3>
            <p>Messages</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.header("📚 Example Queries")
    example_prompts = [
        "What are the latest developments in quantum computing?",
        "Explain the current state of renewable energy adoption worldwide",
        "What is LangGraph and how does it compare to LangChain?",
        "Research the impact of AI on software development in 2024"
    ]
    for i, prompt in enumerate(example_prompts, 1):
        if st.button(f"Example {i}", key=f"example_{i}", use_container_width=True):
            st.session_state.user_input = prompt
            st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Research", "📊 Examples", "📜 History"])

with tab1:
    st.subheader("What would you like to research?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Text input
        user_message = st.text_area(
            "Enter your research query:",
            value=st.session_state.user_input,
            height=100,
            placeholder="E.g., What are the latest developments in artificial intelligence?",
            key="text_area"
        )
    
    with col2:
        st.markdown("**Quick Topics**")
        if st.button("🤖 AI Trends", use_container_width=True):
            st.session_state.user_input = "What are the latest trends in AI and machine learning?"
            st.rerun()
        
        if st.button("💻 Tech News", use_container_width=True):
            st.session_state.user_input = "What are the major tech developments this month?"
            st.rerun()
        
        if st.button("🌍 World News", use_container_width=True):
            st.session_state.user_input = "What are the top global news stories today?"
            st.rerun()
        
        if st.button("🔬 Science", use_container_width=True):
            st.session_state.user_input = "What are recent scientific breakthroughs?"
            st.rerun()
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 3])
    with col_btn1:
        process_button = st.button("🚀 Process Request", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("🗑️ Clear Input", use_container_width=True):
            st.session_state.user_input = ""
            st.rerun()
    with col_btn3:
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.request_count = 0
            st.success("Conversation history cleared!")
            st.rerun()

with tab2:
    st.subheader("🎬 Research Examples")
    st.info("👇 Click any example to see real web search and analysis")
    
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("**🤖 Technology Research**")
        if st.button("Research LangGraph", use_container_width=True, key="demo1"):
            st.session_state.user_input = "What is LangGraph and how is it different from LangChain? Provide technical details and use cases."
            st.rerun()
        
        st.markdown("**🌍 Current Events**")
        if st.button("Latest AI News", use_container_width=True, key="demo2"):
            st.session_state.user_input = "What are the most significant AI developments and announcements in the past month?"
            st.rerun()
    
    with demo_col2:
        st.markdown("**💡 Learning Topics**")
        if st.button("Explain Quantum Computing", use_container_width=True, key="demo3"):
            st.session_state.user_input = "Explain quantum computing in simple terms and discuss its current state and potential applications."
            st.rerun()
        
        st.markdown("**📈 Market Research**")
        if st.button("Renewable Energy Status", use_container_width=True, key="demo4"):
            st.session_state.user_input = "What is the current state of renewable energy adoption globally? Include recent statistics and trends."
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 How It Works")
    st.markdown("""
    1. **Agent analyzes your query** → Understands what information is needed
    2. **Searches the web** → Uses DuckDuckGo to find current, relevant information
    3. **Analyzes results** → Synthesizes information from multiple sources
    4. **Generates response** → Provides comprehensive answer with sources
    
    The agent uses **real web search** (DuckDuckGo), **GPT-4o-mini** for analysis, and **LangGraph** for orchestration.
    """)

with tab3:
    st.subheader("📜 Conversation History")
    
    if st.session_state.conversation_history:
        for i, item in enumerate(reversed(st.session_state.conversation_history), 1):
            with st.expander(f"💬 Conversation {len(st.session_state.conversation_history) - i + 1} - {item['timestamp']}"):
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>
                    {item['user_message']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 Agent:</strong><br>
                    {item['agent_response']}
                </div>
                """, unsafe_allow_html=True)
                
                if item.get('tools_used'):
                    st.markdown("**🔧 Tools Used:**")
                    tools_html = "".join([f'<span class="tool-badge">{tool}</span>' for tool in item['tools_used']])
                    st.markdown(tools_html, unsafe_allow_html=True)
                
                if item.get('sources'):
                    st.markdown("**📚 Sources:**")
                    for source in item['sources'][:3]:
                        st.caption(f"• {source}")
    else:
        st.info("No research history yet. Start researching!")

# Process request
if process_button and user_message:
    # Add to request count
    st.session_state.request_count += 1
    
    # Create placeholder for streaming effect
    with st.container():
        st.markdown("---")
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        tools_placeholder = st.empty()
        details_placeholder = st.empty()
        
        try:
            # Show processing status
            status_placeholder.info("🤔 Agent is thinking...")
            time.sleep(0.5)
            
            # Call API
            start_time = time.time()
            response = requests.post(
                f"{API_URL}/research",
                json={"query": user_message, "depth": "standard"},
                timeout=60  # Research takes longer
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Update status
                status_placeholder.success(f"✅ Request processed in {elapsed_time:.2f}s")
                
                # Display response with animation effect
                response_placeholder.markdown("### 🤖 Agent Response")
                response_container = response_placeholder.container()
                
                # Simulate streaming for better UX
                response_text = result['response']
                displayed_text = ""
                text_placeholder = response_container.empty()
                
                for i in range(0, len(response_text), 15):
                    displayed_text = response_text[:i+15]
                    text_placeholder.markdown(f"""
                    <div class="response-box">
                        {displayed_text}
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.02)
                
                # Final display
                text_placeholder.markdown(f"""
                <div class="response-box">
                    {response_text}
                </div>
                """, unsafe_allow_html=True)
                
                # Tools used
                if result.get('tools_used') and len(result['tools_used']) > 0:
                    tools_placeholder.markdown("### 🔧 Tools Utilized")
                    tools_html = "".join([
                        f'<span class="tool-badge">🛠️ {tool}</span>' 
                        for tool in result['tools_used']
                    ])
                    tools_placeholder.markdown(tools_html, unsafe_allow_html=True)
                else:
                    tools_placeholder.info("ℹ️ No specialized tools were needed for this request")
                
                # Sources
                if result.get('sources') and len(result['sources']) > 0:
                    st.markdown("### 📚 Sources")
                    st.markdown("Information gathered from:")
                    for i, source in enumerate(result['sources'][:5], 1):  # Show top 5
                        st.markdown(f"{i}. [{source}]({source})")
                
                # Save to history
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'user_message': user_message,
                    'agent_response': result['response'],
                    'tools_used': result.get('tools_used', []),
                    'sources': result.get('sources', []),
                    'elapsed_time': elapsed_time
                })
                
                # Metadata
                with details_placeholder.expander("📊 Technical Details"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Response Time", f"{elapsed_time:.2f}s")
                    with col2:
                        st.metric("Tools Used", len(result.get('tools_used', [])))
                    with col3:
                        st.metric("Response Length", f"{len(result['response'])} chars")
                    
                    st.json(result)
                
                # Clear input after successful processing
                st.session_state.user_input = ""
                
            else:
                status_placeholder.error(f"❌ Error: {response.status_code}")
                response_placeholder.write(response.text)
                
        except requests.exceptions.ConnectionError:
            status_placeholder.error("""
            ❌ **Backend Connection Failed**
            
            The Research Assistant backend is not running. Please start it:
            """)
            response_placeholder.code("python backend/main.py", language="bash")
            response_placeholder.info("The backend should be accessible at http://localhost:8000")
            response_placeholder.warning("Make sure you have installed: pip install duckduckgo-search")
        except requests.exceptions.Timeout:
            status_placeholder.error("⏱️ Request timed out. The server might be overloaded. Please try again.")
        except Exception as e:
            status_placeholder.error(f"❌ An unexpected error occurred: {str(e)}")
            response_placeholder.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built with ❤️ using LangGraph, FastAPI & Streamlit
</div>
""", unsafe_allow_html=True)
