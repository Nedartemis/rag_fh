import os
from datetime import datetime
from pathlib import Path

import streamlit as st

import frontend.front_helper as front_helper
from frontend.chatbot import build_chatbot
from frontend.description import build_description
from frontend.filters import Filters, build_filters

PATH_TMP = Path("tmp")


def build_page():

    # description
    build_description("à faire")

    # button upload documents
    uploaded_result = st.file_uploader(
        f"Déposez base documentaire",
        type=["docx", "pdf", "zip"],
        accept_multiple_files=True,
    )
    if uploaded_result:
        print(len(uploaded_result))
        for uploaded_file in uploaded_result:
            if uploaded_file.name.endswith(".zip"):
                front_helper.extract_zip_file(
                    uploaded_file.getvalue(), path_dst=str(PATH_TMP)
                )
            else:
                front_helper.write(
                    uploaded_file.getvalue(),
                    path_dst=PATH_TMP / os.path.basename(uploaded_file.name),
                )

    build_chatbot(label="custom", get_answer=lambda question: f"You said : {question}")
