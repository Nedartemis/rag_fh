from datetime import datetime

import streamlit as st

from backend.rag.saint_amand import RagSaintAmand
from backend.saint_amand.split_page_into_projects import TABLES_HEADER_MAUBEUGE
from frontend.chatbot import build_chatbot
from frontend.description import build_description
from frontend.filters import Filters, build_filters


def ask_question(messages: dict, filters: Filters) -> str:
    question = messages[-1]["content"]

    rag: RagSaintAmand = st.session_state.rag

    answer = rag.ask(question, filters)
    return answer


def dummy_response(messages: dict) -> str:
    question = messages[-1]["content"]
    return f"You said : {question}"


def build_page():

    if "rag" not in st.session_state:
        st.session_state.rag = RagSaintAmand()

    # description
    build_description(
        content="""Posez des questions sur le chantier de Maubeuge.
            Une réponse sourcée et raisonnée sera faite à partir des CRs.
            Pour obtenir une réponse plus pertinente, jouez avec les filtres (dates, projets, numéro de CR)."""
    )

    # filters
    bounds = Filters(
        projects=list(TABLES_HEADER_MAUBEUGE.keys()),
        date_min=datetime(2012, 8, 30),
        date_max=datetime(2016, 8, 26),
        cr_num_min=1,
        cr_num_max=99,
    )
    # default = Filters(
    #     projects=["Lot 2 "],
    #     date_min=bounds.date_min,
    #     date_max=bounds.date_max,
    #     cr_num_min=1,
    #     cr_num_max=91,
    # )
    filters = build_filters(bounds=bounds, default=bounds, label="chrono")

    # chatbot and its buttons
    build_chatbot(
        "maubeuge",
        lambda messages: ask_question(messages, filters),  # ask_question(messages),
    )
