import numpy as np
import pandas as pd

from backend.rag.retriever import SentenceTransformerWrapper
from backend.saint_amand.extract_all_infos import (
    convert_filters_to_args,
    filter_compressed,
    load_df_compressed,
)
from frontend.filters import Filters
from vars import PATH_MODEL_MINI

FILENAME_EMBEDDINGS = "test.pt"


def load_data_retriever() -> pd.DataFrame:
    print("Loading data...")
    df = load_df_compressed()
    df = filter_compressed(
        df, projects_to_extract=["Lot 2 ", "Lot 14 "], cr_num_bounds=(1, 10)
    )

    return df


def numerize_data() -> None:

    # load data
    df = load_data_retriever()

    # load retriever
    print("Loading retriever...")
    retriever = SentenceTransformerWrapper(PATH_MODEL_MINI)

    # encode
    print("Encoding...")
    embeddings = retriever.encode(df["cell"].tolist(), show_progress_bar=True)

    # saving
    print("Saving...")
    retriever.save(embeddings, FILENAME_EMBEDDINGS)


def load_numerization() -> np.ndarray:
    print("Load numerization...")
    return SentenceTransformerWrapper.load_embeddings(filename=FILENAME_EMBEDDINGS)


class Toto:
    def __init__(self):
        self.df = load_data_retriever()
        self.embeddings = load_numerization()
        self.retriever = SentenceTransformerWrapper(PATH_MODEL_MINI)

        assert len(self.df) == self.embeddings.shape[0]

    def compute_order(self, question: str, filters: Filters) -> pd.DataFrame:

        # filter data
        print(f"Len before : {len(self.df)}")
        df = self.df.copy()
        df.index = range(len(df))
        df = filter_compressed(df, **convert_filters_to_args(filters))
        print(f"Len after : {len(df)}")

        # filter embeddings
        embeddings = self.embeddings[df.index]

        assert len(df) == embeddings.shape[0]

        # compute question embeddings
        question_embeddings = self.retriever.encode(question)

        # compute similarity
        similarities = self.retriever.similarity(embeddings, question_embeddings)
        assert similarities.shape == (len(df), 1)

        # join it with all the data
        df["similarity"] = similarities.reshape((len(df),))
        df.sort_values("similarity", ascending=False, inplace=True)

        return df


if __name__ == "__main__":
    numerize_data()
