import os
from datetime import datetime
from pathlib import Path

import streamlit as st

import frontend.helper as helper
from frontend.description import build_description
from frontend.filters import Filters, build_filters

PATH_TMP = Path("tmp")


def build_page():

    # description
    build_description("à faire")

    # filters
    filters = Filters(
        projects=["Lot 1", "Lot 2", "Lot 3"],
        date_min=datetime(2025, 1, 1),
        date_max="today",
        cr_num_min=1,
        cr_num_max=90,
    )
    build_filters(filters, filters)

    # button dowload chronology
    st.download_button(
        label="Télécharger chronologie",
        data=b"Hello world",
        file_name="toto.txt",
    )
