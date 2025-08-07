import streamlit as st

from backend.preprocess_crs.projects import Projects


def build_choose_project() -> Projects:
    return st.selectbox(
        "Choix du chantier",
        options=list(Projects),
        format_func=lambda x: "-".join(s.capitalize() for s in x.name.split("_")),
    )
