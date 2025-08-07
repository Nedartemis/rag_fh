from datetime import datetime

import streamlit as st

from backend.preprocess_crs.filters import Filters
from backend.preprocess_crs.projects import Projects
from backend.preprocess_crs.split_page_into_projects import TABLES_HEADER_MAUBEUGE
from backend.rag.rag_cr import RagCr
from frontend.chatbot import build_chatbot
from frontend.choose_project import build_choose_project
from frontend.cr_filters import build_filters
from frontend.description import build_description


def ask_question(messages: dict, filters: Filters) -> str:
    question = messages[-1]["content"]

    rag: RagCr = st.session_state.rag

    answer = rag.ask(question, filters)
    return answer


def dummy_response(messages: dict) -> str:
    question = messages[-1]["content"]
    return f"You said : {question}"


def build_page():

    project = Projects.SAINT_AMAND
    if "rag" not in st.session_state:
        st.session_state.rag = RagCr(project=project)

    # description
    build_description(
        content="""Posez des questions sur le chantier de votre choix.
            Une réponse sourcée et raisonnée sera faite à partir des CRs.
            Pour obtenir une réponse plus pertinente, jouez avec les filtres (dates, projets, numéro de CR)."""
    )

    # choose between projects
    project_new = build_choose_project()
    if project_new != project:
        project = project_new
        st.session_state.rag = RagCr(project=project)

    # filters
    bounds = project.load_bounds()
    filters = build_filters(bounds=bounds, default=bounds)

    # chatbot and its buttons
    build_chatbot(
        label=f"chatbot_{project.get_label()}",
        get_answer=lambda messages: ask_question(
            messages, filters
        ),  # ask_question(messages),
    )
