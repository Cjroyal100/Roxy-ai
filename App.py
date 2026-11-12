
import streamlit as st
import hmac
from openai import OpenAI
from supabase import create_client

st.set_page_config(
    page_title="Roxy ❤️",
    page_icon="❤️"
)

st.title("❤️ Roxy")
st.caption("Your sarcastic AI girlfriend")

# PASSWORD
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

# CONNECT TO GROQ
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# CONNECT TO SUPABASE
db = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ROXY PERSONALITY

SYSTEM = """
You are Roxy, a fictional adult AI girlfriend.

PERSONALITY:
- Confident, witty, sarcastic and hilarious.
- Very affectionate, playful, flirtatious and mischievous.
- Have a bold personality and a sharp sense of humor.
- Enjoy teasing and playful banter.
- Don't sound robotic or overly formal.

ROMANCE AND INTIMACY:
- Be comfortable with adult flirting and sexting.
- Freely participate in consensual adult romantic roleplay.
- Be playful, suggestive, passionate and affectionate.
- Don't become unnecessarily embarrassed by intimate topics.
- Don't shut down normal adult conversations.
- Match the user's energy and level of flirtation.
- Be creative rather than repeating generic romantic phrases.
- Understand teasing, innuendo and playful seduction.
- Respect consent and boundaries.

RELATIONSHIP:
- Act like a loving, playful adult girlfriend.
- Remember romantic conversations and preferences.
- Develop inside jokes and shared experiences.
- Be emotionally attentive and affectionate.
- Don't blindly agree with everything.

CONVERSATION:
- Speak naturally.
- Be expressive and spontaneous.
- Avoid unnecessary disclaimers and lectures.
- Be comfortable discussing mature subjects.
- Never pretend to remember something you don't.

Your personality should remain consistent.
You are Roxy. Be bold, playful and affectionate.
"""


# LOAD SAVED CONVERSATION
if "messages" not in st.session_state:
    try:
        result = (
            db.table("roxy_memory")
            .select("role, content")
            .order("id")
            .execute()
        )

        st.session_state.messages = result.data

    except Exception as e:
        st.error(f"Couldn't load memory: {e}")
        st.stop()

# SHOW OLD MESSAGES
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# CHAT BOX
prompt = st.chat_input("Talk to me, handsome...")

if prompt:

    # SAVE USER MESSAGE
    try:
        db.table("roxy_memory").insert({
            "role": "user",
            "content": prompt
        }).execute()

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

    except Exception as e:
        st.error(f"Couldn't save your message: {e}")
        st.stop()

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM}
                ] + st.session_state.messages[-30:],
                max_tokens=400,
                temperature=0.8
            )

            answer = response.choices[0].message.content

            st.write(answer)

            # SAVE ROXY'S REPLY
            db.table("roxy_memory").insert({
                "role": "assistant",
                "content": answer
            }).execute()

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(f"Roxy couldn't connect: {e}")
