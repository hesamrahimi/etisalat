import streamlit as st
import time
from datetime import datetime
from typing import Generator, Tuple
import asyncio
from mock_supervisor import MockSupervisor

# Page configuration
st.set_page_config(
    page_title="AI Assistant Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #fafafa;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .ai-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .ai-thoughts {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #667eea;
        font-style: italic;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
        margin-top: 0.5rem;
    }
    
    .input-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

class ChatGUI:
    def __init__(self):
        self.supervisor = MockSupervisor()
        
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'show_thoughts' not in st.session_state:
            st.session_state.show_thoughts = True
        if 'processing' not in st.session_state:
            st.session_state.processing = False
    
    def add_user_message(self, message: str):
        """Add user message to chat history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "type": "user",
            "content": message,
            "timestamp": timestamp
        })
    
    def add_ai_message(self, message: str, is_thought: bool = False):
        """Add AI message to chat history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "type": "ai_thought" if is_thought else "ai_response",
            "content": message,
            "timestamp": timestamp
        })
    
    def display_messages(self):
        """Display all messages in the chat container"""
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                if message["type"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong><br>
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif message["type"] == "ai_thought" and st.session_state.show_thoughts:
                    st.markdown(f"""
                    <div class="ai-thoughts">
                        <strong>🤔 AI Thoughts:</strong><br>
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif message["type"] == "ai_response":
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>🤖 AI Assistant:</strong><br>
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def process_user_input(self, user_input: str):
        """Process user input and get AI response"""
        if not user_input.strip():
            return
        
        # Add user message
        self.add_user_message(user_input)
        
        # Set processing state
        st.session_state.processing = True
        
        # Create placeholders for streaming responses
        thoughts_placeholder = st.empty()
        response_placeholder = st.empty()
        
        # Process with supervisor (mock for now)
        for thought, final_response in self.supervisor.process_input(user_input):
            if thought and st.session_state.show_thoughts:
                self.add_ai_message(thought, is_thought=True)
                # Update display in real-time
                with thoughts_placeholder.container():
                    st.markdown(f"""
                    <div class="ai-thoughts">
                        <strong>🤔 AI Thoughts:</strong><br>
                        {thought}
                        <div class="timestamp">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(0.5)  # Simulate thinking time
            
            if final_response:
                self.add_ai_message(final_response, is_thought=False)
                # Clear placeholders and refresh full display
                thoughts_placeholder.empty()
                response_placeholder.empty()
                break
        
        # Reset processing state
        st.session_state.processing = False
    
    def run(self):
        """Main application loop"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🤖 AI Assistant Chat Interface</h1>
            <p>Intelligent conversations with thought transparency</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-info">
                <h3>🔧 Settings</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.show_thoughts = st.toggle(
                "Show AI Thoughts", 
                value=st.session_state.show_thoughts,
                help="Toggle to show/hide the AI's thinking process"
            )
            
            st.markdown("---")
            
            # Statistics
            st.markdown("""
            <div class="sidebar-info">
                <h3>📊 Chat Statistics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            total_messages = len(st.session_state.messages)
            user_messages = len([m for m in st.session_state.messages if m["type"] == "user"])
            ai_messages = len([m for m in st.session_state.messages if m["type"] == "ai_response"])
            
            st.metric("Total Messages", total_messages)
            st.metric("Your Messages", user_messages)
            st.metric("AI Responses", ai_messages)
            
            st.markdown("---")
            
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
        
        # Main chat area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Chat history display
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            self.display_messages()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Input area
            st.markdown('<div class="input-container">', unsafe_allow_html=True)
            
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_area(
                    "Type your message here...",
                    height=100,
                    placeholder="Ask me anything! I'll show you my thinking process if enabled.",
                    label_visibility="collapsed"
                )
                
                col_submit, col_status = st.columns([1, 2])
                
                with col_submit:
                    submitted = st.form_submit_button(
                        "🚀 Send Message", 
                        disabled=st.session_state.processing,
                        use_container_width=True
                    )
                
                with col_status:
                    if st.session_state.processing:
                        st.info("🔄 AI is thinking...")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process input
            if submitted and user_input and not st.session_state.processing:
                self.process_user_input(user_input)
                st.rerun()
        
        with col2:
            # Help and info
            st.markdown("""
            <div class="sidebar-info">
                <h3>💡 How to Use</h3>
                <ul>
                    <li>Type your message in the text area</li>
                    <li>Click "Send Message" or press Ctrl+Enter</li>
                    <li>Toggle "Show AI Thoughts" to see thinking process</li>
                    <li>Scroll up to see chat history</li>
                    <li>Use "Clear Chat History" to start fresh</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main entry point"""
    chat_gui = ChatGUI()
    chat_gui.run()

if __name__ == "__main__":
    main()