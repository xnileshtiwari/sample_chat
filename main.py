import streamlit as st
import dotenv
import os
import json
from llm import get_completion
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()
        
# Page configuration
st.set_page_config(
    page_title="Idea Spark⚡",
    page_icon="📊",
    layout="centered"
)


def load_custom_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_custom_css("custom.css")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = {}
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "PDF"
if "selected_csv" not in st.session_state:
    st.session_state.selected_csv = None

# Current time for timestamp
st.session_state.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to save feedback to JSON files
def save_feedback(user_input, assistant_response, feedback_type):
    os.makedirs("feedback", exist_ok=True)
    json_file = f"feedback/{feedback_type}.json"
    feedback_data = {
        "user_input": user_input,
        "assistant_response": assistant_response,
        "timestamp": st.session_state.current_time
    }
    existing_data = []
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    existing_data.append(feedback_data)
    with open(json_file, 'w') as f:
        json.dump(existing_data, f, indent=2)

# App title
st.title("Idea Spark ⚡")

# Sidebar for settings
with st.sidebar:
    st.subheader("Controls")
    # Placeholder for mode selection (expand as needed)
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.feedback_given = {}
        st.rerun()

# Sample prompts
st.subheader("Sample Prompts")
pdf_prompts = [
    "💡 Help me brainstorm innovative features for a health tracking mobile app",
    "🧠 I need fresh ideas for engaging remote employees during virtual team meetings",
    "🌱 Let's explore sustainable packaging alternatives for an e-commerce business",
    "🔄 Help me reimagine the traditional university lecture format for online learning"
]
col1, col2 = st.columns(2)
with col1:
    if st.button(pdf_prompts[0], key="prompt1"): st.session_state.temp_input = pdf_prompts[0]
    if st.button(pdf_prompts[2], key="prompt3"): st.session_state.temp_input = pdf_prompts[2]
with col2:
    if st.button(pdf_prompts[1], key="prompt2"): st.session_state.temp_input = pdf_prompts[1]
    if st.button(pdf_prompts[3], key="prompt4"): st.session_state.temp_input = pdf_prompts[3]

# Display chat messages with feedback
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            msg_id = f"msg_{idx // 2}"
            if msg_id not in st.session_state.feedback_given:
                feedback = st.feedback("thumbs", key=f"feedback_{msg_id}")
                if feedback is not None:
                    feedback_type = "disliked" if feedback == 0 else "liked"
                    save_feedback(st.session_state.messages[idx-1]["content"], message["content"], feedback_type)
                    st.session_state.feedback_given[msg_id] = feedback_type
                    st.rerun()
            else:
                feedback_type = st.session_state.feedback_given[msg_id]
                st.caption(f"Thank you for your feedback! ({feedback_type})")

# User input handling
user_input = st.chat_input("Ask me anything ✨...")
if "temp_input" in st.session_state and st.session_state.temp_input:
    user_input = st.session_state.temp_input
    st.session_state.temp_input = None

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Stream assistant response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response_generator = get_completion(st.session_state.messages)
            full_response = st.write_stream(response_generator)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

# Footer
st.markdown("""
<div style="margin-top: 20px; text-align: center; color: #888;">
    <p>Made with ❤️ by Nilesh | Created On: March 24, 2025</p>
</div>
""", unsafe_allow_html=True)
