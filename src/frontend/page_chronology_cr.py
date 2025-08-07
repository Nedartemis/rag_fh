from datetime import datetime

import streamlit as st

import frontend.front_helper as front_helper
from backend.preprocess_crs.filters import Filters
from backend.preprocess_crs.projects import Projects
from backend.preprocess_crs.write_chrono import extract_infos_and_write_doc
from frontend.buttons import build_dowload_event
from frontend.choose_project import build_choose_project
from frontend.cr_filters import build_filters
from frontend.description import build_description
from vars import PATH_TMP


def compute_chrono_bytes(project: Projects, filters: Filters):

    path_docx = PATH_TMP / "chrono.docx"

    # write
    print("Write data...")
    extract_infos_and_write_doc(
        project=project, path_docx_to_write=path_docx, filters=filters
    )

    # load
    bytes = front_helper.read(path_docx)

    return bytes


def build_page():

    # description
    build_description(
        """
        Télécharger l'ensemble des **actions** de chaque projet du chantier **de votre choix**.
        Les actions **identiques** répétées dans plusieurs CRs sont **rassemblées**.
        Les actions sont **rangées par chronologie**.
        Bien que condensées, ces informations restent très **volumineuses**.
        N'hésiter pas à jouer avec les **filtres** pour récupérer les infos qui vous seront utiles sans être submergé.
    """
    )

    # choose between projects
    project = build_choose_project()

    # filters
    bounds = project.load_bounds()
    filters = build_filters(bounds=bounds, default=bounds)

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

    # st.button(
    #     "Télécharger chronologie",
    #     on_click=build_dowload_event(lambda: compute_chrono_bytes(filters), filename),
    # )

    st.markdown(
        """
    <style>
    div.stButton > button {
        width: 100%;
        height: 100%;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    col1.button(
        "Calculer chronologie",
        on_click=lambda: col2.download_button(
            label="Télécharger chronologie",
            data=compute_chrono_bytes(project, filters),
            file_name=filename,
        ),
    )
