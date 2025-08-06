import re
from collections import namedtuple
from typing import List, Tuple

import pandas as pd
from tqdm import tqdm

from backend.saint_amand import TYPE_PAGES
from backend.saint_amand.projects import Projects

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

TABLES_HEADER_MAUBEUGE = {
    # organismes
    "AMVS": "AGGLOMERATION MAUBEUGE VAL DE SAMBRE",
    # "": "AEMCO",
    # "": "ISC",
    "DR": "DUVAL-RAYNAL SARL D'ARCHITECTURE",
    # "": "IN SITU",
    # "": "SEEBAT",
    "BERIM": "BERIM",
    "BERI": "BERIM",
    "ESEC": "ESEC Ingénierie",
    "CTH": "C.T.H.",
    "TESSON": "Henri Tesson",
    "DEKRA": "DEKRA",
    "VERITAS": "BUREAU VERITAS",
    "NAMIXIS": "NAMIXIS",
    # entreprises
    "SOGEA": "SOGEA CARONI SAS",
    "SOG": "SOGEA CARONI SAS",
    "SI 21": "SOLS INDUSTRIELS 21",
    "A&T EUROPE": "A&T EUROPE",
    "VICTOIRE": "VICTOIRE",
    "S.A.M. +": "S.A.M. +",
    "CRI": "CRI",
    "MODULE": "MODULE",
    "SAE": "SAE",
    "AAB": "ATELIER ARTISTIQUE DU BETON",
    "OTIS": "OTIS",
    "LMP": "LMP",
    "MQB": "SA MISSENARD QUINT B",
    "SUEDE SAUNA": "SUEDE SAUNA",
    "SNEF": "SNEF",
    "ELISATH": "ELISATH",
    "POSEIDON": "POSEIDON",
    "EUROENV": "EUROENVIRONNEMENT / TROMONT",
    "TROMONT": "EUROENVIRONNEMENT / TROMONT",
    "MONTARON": "MONTARON Ets",
    # Other
    "COEXIA": "COEXIA",
    "MYRTHA": "MYRTHA",
    "EAS": "EAS",
    "DRD": "DRD",
    "COE": "COE",
}


def _is_start_line_table_saint_amand(line: str) -> bool:
    if line.startswith("Lot"):
        return True
    return any(line.startswith(e + " ") for e in OTHER_TABLES)


def is_start_line_table_maubeuge(line: str) -> bool:
    return any(line.startswith(e) for e in TABLES_HEADER_MAUBEUGE.keys() if e)


def _to_remove_trash_maubeuge(text: str) -> bool:
    return text.startswith("AMVS – Construction d’un centre aquatique intercommunal")


def split_pages_into_projects(
    pages: TYPE_PAGES, df_cr: pd.DataFrame, project: Projects
) -> pd.DataFrame:

    tables: List[dict] = []
    Buffer = namedtuple("Buffer", "start_page text")
    is_start_line_table = {
        Projects.SAINT_AMAND: _is_start_line_table_saint_amand,
        Projects.MAUBEUGE: is_start_line_table_maubeuge,
    }[project]
    offset_table_action = {
        Projects.SAINT_AMAND: 3,
        Projects.MAUBEUGE: 2,
    }[project]
    to_remove = {
        Projects.SAINT_AMAND: lambda x: False,
        Projects.MAUBEUGE: _to_remove_trash_maubeuge,
    }[project]

    # process pages by cr
    for _, row in tqdm(list(df_cr.iterrows()), "Split pages into projects"):
        cr, start, end = row["num_cr"], row["page_start"], row["page_end"]
        lst: List[Tuple[int, int, str]] = []

        buffer = Buffer(None, "")

        # process pages where projects tables are
        for current_page in range(start + offset_table_action, end + 1):

            text = pages[current_page - 1]

            # remove header because it's just noise
            text = re.sub(
                pattern=r"Communauté d’Agglomération des Portes du Hainaut.*\n Page \d* sur \d*",
                repl="",
                string=text,
            )

            # detect and split projects
            for line in [e for e in text.split("\n")]:

                if is_start_line_table(line):  # the start of a project
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
            if is_start_line_table(text) and not to_remove(text)
        )

    return pd.DataFrame(tables)
