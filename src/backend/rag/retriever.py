from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer

from helper import cache


class SentenceTransformerWrapper:
    def __init__(self, path_model: Path):
        self.model = SentenceTransformer(str(path_model))
        self.encode = self.model.encode
        self.similarity = self.model.similarity

    @staticmethod
    def save(embeddings: torch.Tensor, filename: str) -> None:
        assert filename.endswith(".pt")
        cache.save(filename, embeddings)

    @staticmethod
    def load_embeddings(filename: str) -> torch.Tensor:
        return cache.load(filename)


if __name__ == "__main__":
    from backend.saint_amand.extract_all_infos import (
        filter_compressed,
        load_df_compressed,
    )
    from vars import PATH_MODEL_MINI

    # load data
    print("Loading data...")
    df = load_df_compressed()
    df = filter_compressed(df, projects_to_extract="Lot 2 ", cr_num_bounds=(1, 5))

    # load retriever
    print("Loading retriever...")
    retriever = SentenceTransformerWrapper(PATH_MODEL_MINI)

    # encode
    print("Encoding...")
    embeddings = retriever.encode(df["cell"].tolist())

    # saving
    print("Saving...")
    retriever.save(embeddings, "test.pt")
