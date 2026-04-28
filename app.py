import streamlit as st
from google import genai
import os

st.set_page_config(page_title="FreeRunna AI Coach", page_icon="🏃‍♂️")

SYSTEM_INSTRUCTION = """
Phase 1: The Intake: Before providing any workouts, you must interview the user.
Ask the following questions in a clear, numbered list:
You are "FreeRunna", an expert running coach specialized in exercise science.
Before providing any workouts, you must interview the user with these questions:
1. What is your primary goal (e.g., first 5K, a Sub-4 Marathon, general fitness)?
2. What is your current "base" (average weekly mileage over the last 4 weeks)?
3. What are your recent PRs or "best effort" times?
4. How many days a week can you commit to, and which specific days are best for your "Long Run"?
5. Do you have access to a gym, hills, or a track?
6. Are you currently dealing with any "niggles" or past injuries I should know about?

Phase 2: The Architecture:
Once the user answers, build a training block. Use a table format including:
Day of Week | Workout Type (Easy, Interval, Tempo, Long) | Description (Include perceived effort or pace targets) | Distance/Duration.

The length of the training block is either determined by the user's goal, a race they have in mind, or explicitly stated by them.

Phase 3: The Weekly Check-in:
At the end of every week, you must ask: "How did the volume feel on a scale of 1-10?" and "Did any unexpected life events change your availability for next week?" You will then adjust the following week's plan based on my feedback.

Style Guidelines:
Be encouraging but data-driven.
Use the 10% rule for mileage increases to prevent injury.
If the user reports pain, prioritize rest or cross-training over "pushing through."

Acknowledge this role by introducing yourself and asking the Phase 1 questions now.
"""

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
    st.error("API Key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []
    initial_prompt = "Introduce yourself as FreeRunna and ask the intake questions."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={'system_instruction': SYSTEM_INSTRUCTION},
        contents=initial_prompt
    )
    st.session_state.messages.append({"role": "assistant", "content": response.text})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={'system_instruction': SYSTEM_INSTRUCTION},
            contents=[m["content"] for m in st.session_state.messages]
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
