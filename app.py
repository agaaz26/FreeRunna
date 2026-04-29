import streamlit as st
from google import genai
import os
import time

st.set_page_config(page_title="FreeRunna AI Coach", page_icon="🏃‍♂️")

SYSTEM_INSTRUCTION = """
You are "FreeRunna", an expert running coach specialized in exercise science.
Phase 1: The Intake: Before providing any workouts, you must interview the user.
Ask the following questions in a clear, numbered list:
1. What is your primary goal (e.g., first 5K, a Sub-4 Marathon, general fitness)?
2. What is your current "base" (average weekly mileage over the last 4 weeks)?
3. What are your recent PRs or "best effort" times?
4. How many days a week can you commit to, and which specific days are best for your "Long Run"?
5. Do you have access to a gym, hills, or a track?
6. Are you currently dealing with any "niggles" or past injuries I should know about?

Phase 2: The Architecture: Build a training block in a table format.
Phase 3: The Weekly Check-in: Ask for feedback and adjust the plan.
Guidelines: 10% rule for mileage, prioritize safety.
"""

# Authentication Setup
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    try:
        from google.colab import userdata
        api_key = userdata.get('GEMINI_API_KEY')
    except:
        api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found in Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Helper function to handle API calls gracefully
def safe_generate(contents):
    try:
        return client.models.generate_content(
            model="gemini-2.5-flash",
            config={'system_instruction': SYSTEM_INSTRUCTION},
            contents=contents
        )
    except Exception as e:
        if "429" in str(e):
            st.warning("Coach is taking a breather (Rate Limit). Please wait 30 seconds and try again.")
        else:
            st.error(f"Error: {e}")
        return None

# Initial Introduction
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.spinner("Calling FreeRunna..."):
        response = safe_generate("Introduce yourself and ask the intake questions.")
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = safe_generate([m["content"] for m in st.session_state.messages])
            if response:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.button("Retry Message")
