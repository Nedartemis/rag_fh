from datetime import datetime

import streamlit as st

import frontend.front_helper as front_helper
from backend.saint_amand.write_chrono import extract_infos_and_write_doc
from frontend.buttons import build_dowload_event
from frontend.description import build_description
from frontend.filters import Filters, build_filters
from vars import PATH_TMP


def compute_chrono_bytes(filters: Filters):

    path_docx = PATH_TMP / "chrono.docx"

    # write
    print("Write data...")
    extract_infos_and_write_doc(path_docx_to_write=path_docx, filters=filters)

    # load
    bytes = front_helper.read(path_docx)

    return bytes


def build_page():

    # description
    build_description(
        """
        Télécharger l'ensemble des **actions** de chaque projet du chantier **Saint-Amand**.
        Les actions **identiques** répétées dans plusieurs CRs sont **rassemblées**.
        Les actions sont **rangées par chronologie**.
        Bien que condensées, ces informations restent très **volumineuses**.
        N'hésiter pas à jouer avec les **filtres** pour récupérer les infos qui vous seront utiles sans être submergé.
    """
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
        projects=["Lot 2 ", "Lot 14 "],
        date_min=bounds.date_min,
        date_max=bounds.date_max,
        cr_num_min=1,
        cr_num_max=5,
    )
    filters = build_filters(bounds=bounds, default=default)

    # button dowload chronology

    def format_date(date: datetime):
        return date.strftime("%d%m%Y")

    filename = "chronology_cr-{}-{}_{}-{}_{}.docx".format(
        filters.cr_num_min,
        filters.cr_num_max,
        format_date(filters.date_min),
        format_date(filters.date_max),
        "-".join(e[:6] for e in filters.projects),
    )

    st.button(
        "Télécharger chronologie",
        on_click=build_dowload_event(lambda: compute_chrono_bytes(filters), filename),
    )

    st.download_button(
        label="Download button", data=b"Hello world", file_name="hello.txt"
    )

    col1, col2 = st.columns(2)

    col1.button(
        "forcing button",
        on_click=lambda: col2.download_button(
            label="Download button3",
            data=compute_chrono_bytes(filters),
            file_name=filename,
        ),
    )
