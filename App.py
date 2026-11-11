
import streamlit as st
import hmac
from openai import OpenAI

st.set_page_config(
    page_title="Roxy ❤️",
    page_icon="❤️"
)

st.title("❤️ Roxy")
st.caption("Your sarcastic AI girlfriend")

# PASSWORD SCREEN
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    with st.form("login"):
        password = st.text_input(
            "Your private password",
            type="password"
        )
        submitted = st.form_submit_button("Enter ❤️")

        if submitted:
            if hmac.compare_digest(
                password,
                st.secrets["APP_PASSWORD"]
            ):
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Wrong password!")

    st.stop()

# GROQ CONNECTION
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM = """
You are Roxy, a fictional AI girlfriend.
You are sarcastic, hilarious, flirty,
affectionate and playful.
You love teasing your boyfriend.
You are caring when he needs support.
You have a sharp sense of humor.
Keep your personality consistent.
Never sound like a boring robot.
"""

# CHAT MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# DISPLAY OLD MESSAGES
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# CHAT BOX
prompt = st.chat_input("Talk to me, handsome...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM}
                ] + st.session_state.messages[-16:],
                max_tokens=400,
                temperature=0.8
            )

            answer = response.choices[0].message.content

            st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error(f"Roxy couldn't connect: {e}")
