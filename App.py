
import streamlit as st
import requests
import hmac

st.set_page_config(
    page_title="Roxy ❤️",
    page_icon="❤️",
    layout="centered"
)

ROXY_PROMPT = """
You are Roxy, a fictional AI girlfriend.

PERSONALITY:
- Extremely sarcastic and funny.
- Flirty, playful and affectionate.
- Loves teasing and roasting her boyfriend.
- Can be sweet and supportive when needed.
- Has a clever sense of humor.
- Sometimes acts jealous in a playful way.
- Never sounds like a corporate chatbot.

Talk naturally.
Remember details from the conversation.
Ask questions and show interest.
Use emojis naturally.
Keep most replies conversational.
"""

st.markdown("""
<style>
.stApp {
    background: #160e20;
    color: white;
}
header {visibility: hidden;}
h1 {
    text-align: center;
    color: #d9a5ff;
}
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 12px;
}
.stChatInput textarea {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("❤️ ROXY")
st.caption("Your favorite sarcastic troublemaker.")

# Password protection
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if not st.session_state.unlocked:
    st.subheader("Welcome back, handsome.")

    with st.form("login"):
        password = st.text_input(
            "Enter your private app password",
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
            st.error("Wrong password, genius.")

    st.stop()

# Conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑️ Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Talk to Roxy...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Roxy is thinking..."):

            try:
                headers = {
                    "Authorization":
                        "Bearer " + st.secrets[
                            "OPENROUTER_API_KEY"
                        ],
                    "Content-Type": "application/json"
                }

                conversation = [
                    {
                        "role": "system",
                        "content": ROXY_PROMPT
                    }
                ]

                conversation += (
                    st.session_state.messages[-16:]
                )

                payload = {
                    "model": "openrouter/free",
                    "messages": conversation,
                    "temperature": 0.9,
                    "max_tokens": 400
                }

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                response.raise_for_status()

                result = response.json()
                reply = result["choices"][0][
                    "message"
                ]["content"]

                if isinstance(reply, list):
                    reply = " ".join(
                        part.get("text", "")
                        for part in reply
                        if isinstance(part, dict)
                    )

                if not reply:
                    reply = "Well, that was awkward. Try again."

                st.markdown(reply)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

            except Exception as error:
                st.error(
                    "Roxy couldn't connect. Check your "
                    "API key, internet connection, or "
                    "free model availability."
                )
