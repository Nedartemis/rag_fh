import re
from collections import namedtuple
from typing import List, Tuple

import pandas as pd
from tqdm import tqdm

from backend.saint_amand import TYPE_PAGES

OTHER_TABLES = [
    "I – ORDRE DU JOUR DE LA PROCHAINE REUNION",
    "2 – OBSERVATIONS GENERALES",
    "3 – MAITRISE D'OUVRAGE",
    "4 – MAITRISE D'ŒUVRE",
    "OPC",
    "BET STRUCTURE",
    "BET FLUIDES",
    "BET VRD & PAYSAGES",
    "BET ACOUSTIQUE",
    "BUREAU DE CONTRÔLE",
    "SPS",
    "SSI",
    "6 – OBSERVATIONS PAR CORPS D'ÉTAT",
    "TOUS CORPS D’ETATS",
    "VI – ANNEXES",
]


def _is_start_line_table(line: str) -> bool:
    if line.startswith("Lot"):
        return True
    return any(line.startswith(e + " ") for e in OTHER_TABLES)


def split_pages_into_projects(pages: TYPE_PAGES, df_cr: pd.DataFrame) -> pd.DataFrame:

    tables: List[dict] = []
    Buffer = namedtuple("Buffer", "start_page text")

    # process pages by cr
    for _, row in tqdm(list(df_cr.iterrows()), "Split pages into projects"):
        cr, start, end = row["num_cr"], row["page_start"], row["page_end"]
        lst: List[Tuple[int, int, str]] = []

        buffer = Buffer(None, "")

        # process pages where projects tables are
        for current_page in range(start + 3, end + 1):

            text = pages[current_page - 1]

            # remove header because it's just noise
            text = re.sub(
                pattern=r"Communauté d’Agglomération des Portes du Hainaut.*\n Page \d* sur \d*",
                repl="",
                string=text,
            )

            # detect and split projects
            for line in [e for e in text.split("\n")]:

                if _is_start_line_table(line):  # the start of a project
                    # store the buffer
                    lst.append((buffer.start_page, current_page, buffer.text))
                    # reset the buffer
                    buffer = Buffer(current_page, line)
                else:  # the middle/end of a project
                    # fill the buffer
                    buffer = Buffer(buffer.start_page, buffer.text + "\n" + line)

        # store the last one
        lst.append((buffer.start_page, current_page, buffer.text))

        # remove those that are not projects
        tables.extend(
            {
                "num_cr": cr,
                "page_table_start": page_start,
                "page_table_end": page_end,
                "text_table": text,
            }
            for page_start, page_end, text in lst
            if _is_start_line_table(text)
        )

    return pd.DataFrame(tables)
