import os
from abc import abstractmethod
from datetime import datetime
from typing import Callable, List

import numpy as np
import pandas as pd

from backend.rag.claude_client import ClaudeClient
from backend.rag.retriever import SentenceTransformerWrapper
from frontend.filters import Filters
from vars import PATH_MODEL_MINI


class RagPipeline:

    def __init__(self):
        # retriever
        self.retriever = SentenceTransformerWrapper(PATH_MODEL_MINI)

        # init LLM
        self.llm = ClaudeClient(os.environ["CLAUDE_KEY"])

    @abstractmethod
    def format_chunks(self, df: pd.DataFrame) -> List[str]:
        pass

    @abstractmethod
    def get_instructions(self) -> List[str]:
        pass

    @abstractmethod
    def get_n(self) -> int:
        pass

    def _ask(
        self,
        question: str,
        df: pd.DataFrame,
        embeddings: np.ndarray,
    ) -> str:

        # check consistency
        assert len(df) == embeddings.shape[0]

        # compute question embeddings
        question_embeddings = self.retriever.encode(question)

        # compute similarity
        similarities = self.retriever.similarity(embeddings, question_embeddings)
        assert similarities.shape == (len(df), 1)

        # join it with all the data
        df["similarity"] = similarities.reshape((len(df),))
        df.sort_values("similarity", ascending=False, inplace=True)

        # keep n top chunks
        print(df)
        df = df.iloc[: self.get_n()]

        # format chunks
        contexts = self.format_chunks(df)

        # ask the llm
        m = f"""Utilisez les informations suivantes :
            {'\n\n--------------------\n\n'.join(contexts)}

            pour répondre à cette question :
            {question}

            Ne pas inclure tout ce qui ne semble pas pertinent.
            {'\n'.join(self.get_instructions())}.
        """
        print(m)

        messages = [{"role": "user", "content": m}]
        result = self.llm.create_message(messages=messages)

        # return
        answer = result["content"][0]["text"]

        print("-----------------\nResult\n\n")
        print(answer)

        return answer


if __name__ == "__main__":

    pass
