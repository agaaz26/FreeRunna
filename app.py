import streamlit as st
from google import genai
import os

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
"""

api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Using 1.5 Flash here for more stable free-tier limits
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config={'system_instruction': SYSTEM_INSTRUCTION},
            contents="Introduce yourself and ask the intake questions."
        )
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Quota error: {e}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                config={'system_instruction': SYSTEM_INSTRUCTION},
                contents=[m["content"] for m in st.session_state.messages]
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Rate limit hit. Wait 60 seconds.")
