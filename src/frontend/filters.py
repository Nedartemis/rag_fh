from dataclasses import dataclass
from datetime import datetime
from typing import List

import streamlit as st


@dataclass
class Filters:
    projects: List[str]
    date_min: datetime
    date_max: datetime
    cr_num_min: int
    cr_num_max: int


def build_filters(bounds: Filters, default: Filters) -> Filters:

    # --- POP-UP RÉGLAGES
    with st.expander("⚙️ Filtres", expanded=False):
        # 1. Liste déroulante
        projects = st.multiselect(
            "Choisissez un/des projet(s) :", bounds.projects, default=default.projects
        )

        # 2. Date min / max
        col1, col2 = st.columns(2)
        with col1:
            date_min = st.date_input(
                "Date action minimum",
                value=default.date_min,
                min_value=default.date_min,
                max_value=default.date_max,
            )
        with col2:
            date_max = st.date_input(
                "Date action maximum",
                value=default.date_max,
                min_value=default.date_min,
                max_value=default.date_max,
            )

        # 3. Nombre min / max
        number_min, number_max = st.slider(
            "Sélectionnez une plage de valeurs numériques :",
            min_value=bounds.cr_num_min,
            max_value=bounds.cr_num_max,
            value=(default.cr_num_min, default.cr_num_max),
        )

        # Affichage des valeurs choisies (facultatif)
        st.markdown(f"✅ Projet sélectionnée : **{', '.join(projects)}**")
        st.markdown(f"📅 Plage de dates : **{date_min}** → **{date_max}**")
        st.markdown(f"🔢 Plage numérique : {number_min} → **{number_max}**")

    return Filters(
        projects=projects,
        date_min=date_min,
        date_max=date_max,
        cr_num_min=number_min,
        cr_num_max=number_max,
    )
