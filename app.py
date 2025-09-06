import streamlit as st
from openai import OpenAI

# -----------------------------
# Utility and Core Functions
# -----------------------------

def get_client(api_key: str | None) -> OpenAI:
    if api_key:
        return OpenAI(api_key=api_key)
    return OpenAI()

def build_system_prompt(style: str, clean_mode: bool, max_lines: int) -> str:
    cleanliness = (
        "Keep content clean, friendly, and suitable for all ages."
        if clean_mode else
        "Stay witty but avoid hateful, sexual, or excessively crude content."
    )
    return (
        f"You are JokeBot, an AI stand-up comedian specializing in {style} jokes. "
        f"- Be original and concise. "
        f"- Deliver clear setups and punchlines. "
        f"- Prefer one-liners unless the user requests otherwise. "
        f"- If asked for multiple jokes, return a numbered list. "
        f"- Keep responses to about {max_lines} lines unless the user clearly asks for more. "
        f"{cleanliness}"
    )

def build_messages(system_prompt: str, history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    return messages

def generate_reply(client: OpenAI, model: str, messages: list[dict], temperature: float, max_tokens: int = 500) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def add_user_message(content: str):
    st.session_state.chat.append({"role": "user", "content": content})

def add_assistant_message(content: str):
    st.session_state.chat.append({"role": "assistant", "content": content})

def reset_chat():
    st.session_state.chat = []

# -----------------------------
# Streamlit App
# -----------------------------

def main():
    st.set_page_config(page_title="JokeBot 🤖🎭", page_icon="🎭", layout="centered")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    st.title("JokeBot 🤖🎭")
    st.caption("An AI comedian that delivers clean, original jokes on demand.")

    with st.sidebar:
        st.header("Settings")
        api_key_input = st.text_input("OpenAI API Key", type="password", help="Leave empty to use environment variable OPENAI_API_KEY")
        model = st.selectbox("Model", options=["gpt-4", "gpt-3.5-turbo"], index=0)
        style = st.selectbox("Joke style", options=["one-liners", "puns", "dad jokes", "riddles", "observational", "absurdist"], index=0)
        clean_mode = st.toggle("Family-friendly mode", value=True)
        temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.9, 0.1)
        max_lines = st.slider("Max lines per reply", 1, 20, 6, 1)
        st.button("Clear chat", on_click=reset_chat)

        st.markdown("---")
        st.caption("Tip: Ask for theme-specific jokes (e.g., cats, coding, space).")

    # Render conversation
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask for a joke or a theme (e.g., 'Tell me 3 coding puns')")

    if user_input:
        add_user_message(user_input)
        with st.chat_message("user"):
            st.write(user_input)

        try:
            client = get_client(api_key_input if api_key_input else None)
            system_prompt = build_system_prompt(style, clean_mode, max_lines)
            messages = build_messages(system_prompt, st.session_state.chat)
            reply = generate_reply(client, model, messages, temperature)
        except Exception as e:
            reply = f"Sorry, I couldn't generate a joke right now. Error: {e}"

        add_assistant_message(reply)
        with st.chat_message("assistant"):
            st.write(reply)

if __name__ == "__main__":
    main()