import os
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st
from streamlit.elements.widgets.audio_input import UploadedFile

import frontend.front_helper as front_helper
from backend.rag.rag_custom import RagCustom
from frontend.chatbot import build_chatbot
from frontend.description import build_description
from vars import PATH_TMP

PATH_TO_UPLOAD = PATH_TMP / "custom_rag"


def ask_question(messages: dict, uploaded_files: List[UploadedFile]) -> str:
    question = messages[-1]["content"]

    # remove previous
    for filename in os.listdir(PATH_TO_UPLOAD):
        if filename == ".gitkeep":
            continue
        os.remove(PATH_TO_UPLOAD / filename)

    # download
    for uploaded_file in uploaded_files:
        print("Download files...")
        if uploaded_file.name.endswith(".zip"):
            front_helper.extract_zip_file(
                uploaded_file.getvalue(), path_dst=str(PATH_TO_UPLOAD)
            )
        else:
            front_helper.write(
                uploaded_file.getvalue(),
                path_dst=PATH_TO_UPLOAD / os.path.basename(uploaded_file.name),
            )

    # compute path files
    path_files = [
        PATH_TO_UPLOAD / filename
        for filename in os.listdir(PATH_TO_UPLOAD)
        if filename != ".gitkeep"
    ]
    print(path_files)

    rag: RagCustom = st.session_state.rag_custom
    answer = rag.ask(question, path_files)

    return answer


def build_page():

    if not "rag_custom" in st.session_state:
        st.session_state.rag_custom = RagCustom()

    # description
    build_description(
        "Déposez des fichers, posez une question et vous recevrez une réponse raisonnée se basant sur la base documentaire que vous aurez constituée. "
        "Vous pourvez déposer des fichiers word, pdf, txt ou zip (qui compresse les trois précédents formats de fichier)."
    )

    # button upload documents
    uploaded_result = st.file_uploader(
        f"Déposez base documentaire",
        type=["docx", "pdf", "txt", "zip"],
        accept_multiple_files=True,
    )
    if uploaded_result:
        print(len(uploaded_result))

    build_chatbot(
        label="custom",
        get_answer=lambda messages: ask_question(messages, uploaded_result),
    )
    # get_answer=lambda question: f"You said : {question}")
