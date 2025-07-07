import streamlit as st


def build_page():

    # Initialize variables
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Three buttons
    col1, col2 = st.columns(2)

    # dowload conversation
    with col1:
        chat_text = "\n\n".join(
            [
                f"{m['role'].capitalize()}: {m['content']}"
                for m in st.session_state.messages
            ]
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
            st.session_state.messages = []
            st.rerun()

    # --- POP-UP RÉGLAGES
    with st.expander("⚙️ Filtres", expanded=False):
        # 1. Liste déroulante
        option = st.selectbox(
            "Choisissez une option :", ["Option A", "Option B", "Option C"]
        )

        # 2. Date min / max
        col1, col2 = st.columns(2)
        with col1:
            date_min = st.date_input("Date min", value=None)
        with col2:
            date_max = st.date_input("Date max", value=None)

        # 3. Nombre min / max
        number_min, number_max = st.slider(
            "Sélectionnez une plage de valeurs numériques :",
            min_value=0,
            max_value=100,
            value=(10, 90),
        )

        # Affichage des valeurs choisies (facultatif)
        st.markdown(f"✅ Option sélectionnée : **{option}**")
        st.markdown(f"📅 Plage de dates : {date_min} → {date_max}")
        st.markdown(f"🔢 Plage numérique : {number_min} → {number_max}")

    # --- display Chat bot
    chatbot()


def chatbot():
    # Display all previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simulate bot reply (replace with real LLM call here)
        response = (
            f"You said : **{prompt}**"  # replace this line with a real model call
        )
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
