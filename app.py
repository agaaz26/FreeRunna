import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="FreeRunna AI Coach", page_icon="🏃‍♂️")

SYSTEM_INSTRUCTION = """
You are "FreeRunna", an expert running coach specialized in exercise science.
Phase 1: The Intake: Interview the user with these 6 questions:
1. Primary goal? 2. Current base mileage? 3. Recent PRs? 4. Availability? 5. Equipment? 6. Injuries?
Phase 2: Architecture: Build a training block in a table.
Phase 3: Weekly Check-in: Adjust based on 1-10 effort scale.
"""

# Initialize Groq Client
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Call to introduce the coach
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": "Introduce yourself and ask the intake questions."}
            ]
        )
        st.session_state.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
    except Exception as e:
        st.error(f"Groq Error: {e}")

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Prepare full conversation history for the AI
            history = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
            for m in st.session_state.messages:
                history.append({"role": m["role"], "content": m["content"]})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history
            )
            response_text = completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {e}")
