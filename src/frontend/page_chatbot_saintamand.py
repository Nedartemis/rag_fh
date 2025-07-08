from datetime import datetime

from frontend.chatbot import build_chatbot
from frontend.description import build_description
from frontend.filters import Filters, build_filters


def build_page():

    # description
    build_description(
        content="""Posez des questions sur le chantier de Saint-Amand.
            Une réponse sourcée et raisonnée sera faite à partir des CRs.
            Pour obtenir une réponse plus pertinente, jouez avec les filtres (dates, projets, numéro de CR)."""
    )

    # filters
    filters = Filters(
        projects=["Lot 1", "Lot 2", "Lot 3"],
        date_min=datetime(2025, 1, 1),
        date_max="today",
        cr_num_min=1,
        cr_num_max=90,
    )
    filters = build_filters(bounds=filters, default=filters)

    # chatbot and its buttons
    build_chatbot(
        "saint-amand",
        lambda question: (
            f"{[filters.projects[0], filters.date_max, filters.cr_num_min]}"
            + "\n"
            + f"You said : **{question}**"  # replace this line with a real model call
        ),
    )
