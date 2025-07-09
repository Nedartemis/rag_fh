from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from backend.saint_amand.extract_all_infos import extract_infos_saint_amand
from helper.write_docx import LIGHT_BLUE, LIGHT_GREY, WD_PARAGRAPH_ALIGNMENT, DocxWriter
from vars import PATH_DOCS


def write_chrono(dfs_compress: List[pd.DataFrame], path_docx: Path) -> None:

    # pre-process
    titles = [df["title"].iloc[0] for df in dfs_compress]
    dfs_compress = [df.copy().drop("title", axis="columns") for df in dfs_compress]

    # init vars
    columns = ["cell", "dates", "nums_cr", "pages"]
    columns_final_name = ["Action", "Date", "Numéros CR", "Pages"]

    # -- Checks --
    for df in dfs_compress:
        if len(df.columns) != len(columns) or any(
            col not in df.columns for col in columns
        ):
            raise ValueError(f"Expected  : {columns} ; Actual : {df.columns}")

    # -- Create doc --
    doc = DocxWriter()

    # --- Title ---
    nums_cr = np.concat([nums_cr for df in dfs_compress for nums_cr in df["nums_cr"]])
    doc.add_text(
        content=f"Saint Amand résumé CR {nums_cr.min()}-{nums_cr.max()}",
        fontsize=18,
        alignement=WD_PARAGRAPH_ALIGNMENT.CENTER,
    )

    doc.add_newline()

    for title, df in zip(titles, dfs_compress):
        # --- Sub-title ---
        doc.add_text(content=title, fontsize=14, underline=True)

        doc.add_newline()

        # --- Table ---

        # pre-process
        df = df.copy()
        df.rename(
            columns={old: new for old, new in zip(columns, columns_final_name)},
            inplace=True,
        )

        df["dates"] = df["dates"].apply(
            lambda dates: ", ".join(date.strftime("%d-%m-%Y") for date in dates)
        )
        for col in ["nums_cr", "pages"]:
            df[col] = df[col].apply(lambda lst: ", ".join(str(e) for e in lst))

        # docx
        doc.add_table(df, color_header=LIGHT_BLUE, color_cells=LIGHT_GREY)

        doc.add_newline()

    # Enregistrement
    doc.save(path_docx)


def extract_infos_and_write_doc(path_saint_amand: Path, path_docx: Path) -> None:

    # extract
    _, _, dfs_compress = extract_infos_saint_amand(
        path_saint_amand, projects_to_extract="Lot 2 ", cr_num_bounds=(1, 5)
    )

    # write
    dfs_compress = [
        df.rename(columns={"pages_table_start": "pages"}) for df in dfs_compress
    ]
    write_chrono(dfs_compress, path_docx)


if __name__ == "__main__":
    extract_infos_and_write_doc(
        PATH_DOCS / "intégrale CR chantier Saint Amand.pdf", "test.docx"
    )
