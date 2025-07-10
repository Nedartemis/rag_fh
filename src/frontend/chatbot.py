from typing import Any, Callable, Dict

import streamlit as st


def build_chatbot(label: str, get_answer: Callable[[dict], str]):

    def get_messages() -> list:
        return st.session_state.chat_bot_messages[label]

    def reset_messages() -> None:
        st.session_state.chat_bot_messages[label] = []

    def append_message(role: str, content: str) -> None:
        st.session_state.chat_bot_messages[label].append(
            {"role": role, "content": content}
        )

    if "chat_bot_messages" not in st.session_state:
        st.session_state.chat_bot_messages = {}

    if not label in st.session_state.chat_bot_messages:
        reset_messages()

    # --- Two buttons
    col1, col2 = st.columns(2)

    st.markdown(
        """
    <style>
    div.stButton > button {
        width: 100%;
        height: 100%;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # dowload conversation
    with col1:
        chat_text = "\n\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in get_messages()]
        )
        st.download_button(
            label="📥 Télécharger la conversation",
            data=chat_text,
            file_name="conversation.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # clear conversation
    with col2:
        if st.button("🧹 Effacer la conversation", use_container_width=True):
            reset_messages()
            st.rerun()

    # Display all previous messages
    # with big_container:
    for msg in get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Store user message
        append_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simulate bot reply (replace with real LLM call here)
        response = get_answer(get_messages())
        append_message("assistant", response)
        with st.chat_message("assistant"):
            st.markdown(response)
            # st.text_area(
            #     "Click to copy the response", response, height=100, key="copy_response"
            # )

            # st.code(response, language="")  # Enables copy button automatically
            st.rerun()
