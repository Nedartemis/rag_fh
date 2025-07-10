from datetime import datetime

import streamlit as st

from backend.rag.rag_pipeline import RagPipeline
from frontend.chatbot import build_chatbot
from frontend.description import build_description
from frontend.filters import Filters, build_filters


def ask_question(messages: dict, filters: Filters) -> str:
    question = messages[-1]["content"]

    rag: RagPipeline = st.session_state.rag

    answer = rag.ask(question, filters)

    return answer


def dummy_response(messages: dict, filters) -> str:
    question = messages[-1]["content"]
    return f"You said : {question}"


def build_page():

    if "rag" not in st.session_state:
        st.session_state.rag = RagPipeline()

    # description
    build_description(
        content="""Posez des questions sur le chantier de Saint-Amand.
            Une réponse sourcée et raisonnée sera faite à partir des CRs.
            Pour obtenir une réponse plus pertinente, jouez avec les filtres (dates, projets, numéro de CR)."""
    )

    # filters
    bounds = Filters(
        projects=["Lot 2 ", "Lot 14 ", "Lot 24 "],
        date_min=datetime(2011, 3, 15),
        date_max=datetime(2013, 11, 21),
        cr_num_min=1,
        cr_num_max=91,
    )
    default = Filters(
        projects=["Lot 2 "],
        date_min=bounds.date_min,
        date_max=bounds.date_max,
        cr_num_min=1,
        cr_num_max=5,
    )
    filters = build_filters(bounds=bounds, default=default)

    # chatbot and its buttons
    build_chatbot(
        "saint-amand",
        lambda messages: ask_question(
            messages, filters
        ),  # ask_question(messages, filters=filters),
    )
