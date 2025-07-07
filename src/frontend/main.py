import sys

sys.path.append("src/")

import streamlit as st

from frontend import page_chatbot_saintamand

PAGE1 = "Question-Réponse  \nSaint-Amand"
PAGE2 = "Chronologie  \nSaint-Amand"
PAGE3 = "Question-Réponse  \nPersonalisable"

# --- Initialize selected page in session state
if "page" not in st.session_state:
    st.session_state.page = PAGE1

# st.set_page_config(layout="wide")

# --- Navigation Buttons at the Top (Rectangles)
st.markdown(
    """
<style>
div.stButton > button {
    width: 100%;
    height: 60px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
}
</style>
""",
    unsafe_allow_html=True,
)
col1, col2, col3 = st.columns(3)


with col1:
    if st.button(PAGE1):
        st.session_state.page = PAGE1

with col2:
    if st.button(PAGE2):
        st.session_state.page = PAGE2

with col3:
    if st.button(PAGE3):
        st.session_state.page = PAGE3

# --- Render Current Page Content
st.markdown(f"## {st.session_state.page.replace("  \n", " | ")}")

if st.session_state.page == PAGE1:
    page_chatbot_saintamand.build_page()
elif st.session_state.page == PAGE2:
    st.write("This is Page 2. Different content goes here.")
elif st.session_state.page == PAGE3:
    st.write("Now on Page 3. Enjoy this content.")
