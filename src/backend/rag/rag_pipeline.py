import os
from datetime import datetime

from backend.rag.claude_client import ClaudeClient
from backend.rag.saint_amand import Toto
from frontend.filters import Filters


class RagPipeline:

    def __init__(self):
        # init documentary base and retriever
        self.toto = Toto()

        # init LLM
        self.llm = ClaudeClient(os.environ["CLAUDE_KEY"])

    def ask(self, question: str, filters: Filters) -> str:
        # retrieve order among the documentary base
        df = self.toto.compute_order(question, filters)

        # keep n chunks
        print(df)
        df = df.iloc[:10]
        best_chunks = df["cell"].tolist()

        contexts = [
            f"""Nom projet {titre} ; Numéro CR {', '.join(str(num) for num in nums_cr)} ;
            Pages {', '.join(str(page) for page in pages)} :
            {content}"""
            for titre, nums_cr, pages, content in zip(
                df["title"], df["nums_cr"], df["pages_table_start"], df["cell"]
            )
        ]

        # ask the llm
        m = f"""Utilisez les informations suivantes :
            {'\n\n--------------------\n\n'.join(contexts)}

            pour répondre à cette question :
            {question}

            Ne pas inclure tout ce qui ne semble pas pertinent.
            Bien mettre les sources de l'information (nom projet, numéro cr et pages).
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
    import fire

    rag = RagPipeline()
    res = rag.ask(
        "Quelles sont les aléas survenus ?",
        Filters(
            projects=["Lot 2 ", "Lot 14 "],
            date_min=datetime(2011, 3, 15),
            date_max=datetime(2013, 11, 21),
            cr_num_min=1,
            cr_num_max=5,
        ),
    )
    print(res)
