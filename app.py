import streamlit as st
import os
from dotenv import load_dotenv
from mistralai import Mistral

# Load .env for local development
load_dotenv()

# Page config
st.set_page_config(
    page_title="Build Bridge",
    page_icon="🌉",
    layout="centered"
)

st.title("🌉 Build Bridge")
st.markdown("_Your personal coding project mentor — bridging your courses to real projects_")

# === SECURELY LOAD SECRETS ===
api_key = os.getenv("MISTRAL_API_KEY")
agent_id = os.getenv("MISTRAL_AGENT_ID")

# Fallback to st.secrets when deployed
if not api_key or not agent_id:
    try:
        if "MISTRAL_API_KEY" in st.secrets:
            api_key = st.secrets["MISTRAL_API_KEY"]
        if "MISTRAL_AGENT_ID" in st.secrets:
            agent_id = st.secrets["MISTRAL_AGENT_ID"]
    except FileNotFoundError:
        pass

# Validation
if not api_key:
    st.error("❌ Missing Mistral API Key")
    st.info("Add `MISTRAL_API_KEY` to your `.env` file (local) or Streamlit secrets (deployed).")
    st.stop()

if not agent_id:
    st.error("❌ Missing Agent ID")
    st.info("Add `MISTRAL_AGENT_ID` to your `.env` file (local) or Streamlit secrets (deployed).")
    st.stop()

# Initialize Mistral client
client = Mistral(api_key=api_key)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! 👋\n\nI'm Bridge 🦉, your friendly coding mentor!\n\nTell me  what kind of adventure do you want to have today! 🎉"
        }
    ]

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Share your progress, ask for help, or tell me your skills..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Bridge is thinking... 🦉"):
            try:
                if st.session_state.conversation_id is None:
                    # Start new conversation
                    response = client.beta.conversations.start(
                        agent_id=agent_id,
                        inputs=[{"role": "user", "content": prompt}]
                    )
                    # Correct attribute name
                    st.session_state.conversation_id = response.conversation_id
                else:
                    # Continue existing conversation
                    response = client.beta.conversations.append(
                        conversation_id=st.session_state.conversation_id,
                        inputs=[{"role": "user", "content": prompt}]
                    )

                # Extract clean text content
                raw_output = response.outputs[-1].content

                if isinstance(raw_output, list):
                    clean_content = "".join(
                        item.get("text", "") for item in raw_output if item.get("type") == "text"
                    )
                else:
                    clean_content = str(raw_output)

                st.markdown(clean_content)
                st.session_state.messages.append({"role": "assistant", "content": clean_content})

            except Exception as e:
                st.error(f"Oops! Something went wrong: {str(e)}")
                st.info("Check your Agent ID, API key, and internet connection.")

# "Start New Project" button
if st.button("🆕 Start a New Project (clear chat)"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! 👋\n\nI'm Bridge 🦉, your friendly coding mentor!\n\nTell me  what kind of adventure do you want to have today! 🎉"
        }
    ]
    st.session_state.conversation_id = None
    st.rerun()