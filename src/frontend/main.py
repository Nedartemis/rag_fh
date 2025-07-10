import sys

sys.path.append("src/")

import streamlit as st

from frontend import (
    page_chatbot_custom,
    page_chatbot_saintamand,
    page_chronology_saintamand,
)

PAGE1 = "Question-Réponse  \nSaint-Amand"
PAGE2 = "Chronologie  \nSaint-Amand"
PAGE3 = "Question-Réponse  \nPersonalisable"

# --- Initialize selected page in session state
if "page" not in st.session_state:
    st.session_state.page = PAGE2

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
cols = st.columns(3)

pages_details = list(
    zip(
        cols,
        [PAGE1, PAGE2, PAGE3],
        [
            page_chatbot_saintamand.build_page,
            page_chronology_saintamand.build_page,
            page_chatbot_custom.build_page,
        ],
    )
)

for col, page, _ in pages_details:
    with col:
        type = "primary" if st.session_state.page == page else "secondary"
        if st.button(page, type=type):
            st.session_state.page = page
            st.rerun()

# --- Render Current Page Content
st.markdown(f"## {st.session_state.page.replace("  \n", " | ")}")

for _, page, build_page in pages_details:
    if st.session_state.page == page:
        build_page()
        break
