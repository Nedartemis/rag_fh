from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

from backend.preprocess_crs.extract_all_infos import (
    convert_filters_to_args,
    filter_compressed,
    load_df_compressed,
)
from backend.preprocess_crs.filters import Filters
from backend.preprocess_crs.projects import Projects
from backend.rag.rag_pipeline import RagPipeline
from backend.rag.retriever import SentenceTransformerWrapper
from vars import PATH_MODEL_MINI

FILENAME_EMBEDDINGS = "embeddings_{label}.pt"


def load_data_retriever(project: Projects) -> pd.DataFrame:
    print("Loading data...")
    df = load_df_compressed(project)
    df = filter_compressed(
        df,
        projects_to_extract=None,  # projects_to_extract=["Lot 2 ", "Lot 14 "], cr_num_bounds=(1, 10)
    )

    return df


def numerize_data(project: Projects) -> None:

    # load data
    df = load_data_retriever(project)

    # load retriever
    print("Loading retriever...")
    retriever = SentenceTransformerWrapper(PATH_MODEL_MINI)

    # encode
    print("Encoding...")
    embeddings = retriever.encode(df["cell"].tolist(), show_progress_bar=True)

    # saving
    print("Saving...")
    retriever.save(embeddings, FILENAME_EMBEDDINGS.format(label=project.get_label()))


def load_numerization(project: Projects) -> np.ndarray:
    print("Load numerization...")
    return SentenceTransformerWrapper.load_embeddings(
        filename=FILENAME_EMBEDDINGS.format(label=project.get_label())
    )


class RagCr(RagPipeline):
    def __init__(self, project: Projects):
        super().__init__()
        self.df = load_data_retriever(project)
        self.embeddings = load_numerization(project)

        assert len(self.df) == self.embeddings.shape[0]

    def get_instructions(self):
        return [
            "Bien mettre les sources de l'information (nom projet, numéro cr et pages)"
        ]

    def format_chunks(self, df):
        return [
            f"""Nom projet {titre} ; Numéro CR {', '.join(str(num) for num in nums_cr)} ;
            Pages {', '.join(str(page) for page in pages)} :
            {content}"""
            for titre, nums_cr, pages, content in zip(
                df["title"], df["nums_cr"], df["pages_table_start"], df["cell"]
            )
        ]

    def get_n(self) -> int:
        return 30

    def ask(self, question: str, filters: Filters) -> Tuple[pd.DataFrame, np.ndarray]:

        # filter data
        print(f"Len before : {len(self.df)}")
        df = self.df.copy()
        df.index = range(len(df))
        df = filter_compressed(df, **convert_filters_to_args(filters))
        print(f"Len after : {len(df)}")

        # filter embeddings
        embeddings = self.embeddings[df.index]

        return super()._ask(question, df, embeddings)


if __name__ == "__main__":
    if True:
        numerize_data(Projects.SAINT_AMAND)
    else:
        rag_cr = RagCr()

        question = "Quelles sont les aléas survenus ?"
        filters = Filters(
            projects=["Lot 2 ", "Lot 14 "],
            date_min=datetime(2011, 3, 15),
            date_max=datetime(2013, 11, 21),
            cr_num_min=1,
            cr_num_max=5,
        )
        rag_cr.ask(question, filters)
