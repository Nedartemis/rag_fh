from pathlib import Path
from typing import Tuple

import pandas as pd

from backend.saint_amand.extract_all_infos import (
    convert_filters_to_args,
    extract_infos_saint_amand,
    filter_compressed,
    load_df_compressed,
)
from frontend.filters import Filters
from helper.write_docx import LIGHT_BLUE, LIGHT_GREY, WD_PARAGRAPH_ALIGNMENT, DocxWriter
from vars import PATH_TMP


def write_chrono(
    df_compressed: pd.DataFrame, path_docx: Path, cr_num_bounds: Tuple[int, int]
) -> None:

    # pre-process
    df_compressed = df_compressed.copy()
    titles = df_compressed["title"].unique()

    # init vars
    columns = ["cell", "dates", "nums_cr", "pages", "line_order"]
    columns_final_name = ["Action", "Date", "Numéros CR", "Pages"]

    # -- Checks --
    if any(col not in df_compressed.columns for col in columns):
        raise ValueError(f"Expected  : {columns} ; Actual : {df_compressed.columns}")

    # -- Create doc --
    doc = DocxWriter()

    # --- Title ---
    doc.add_text(
        content=f"Saint Amand résumé CR {cr_num_bounds[0]}-{cr_num_bounds[1]}",
        fontsize=18,
        alignement=WD_PARAGRAPH_ALIGNMENT.CENTER,
    )

    doc.add_newline()

    for title in titles:
        df = df_compressed[df_compressed["title"] == title]

        # --- Sub-title ---
        doc.add_text(content=title, fontsize=14, underline=True)

        doc.add_newline()

        # --- Table ---

        # - pre-process
        df = df.copy()

        # sort
        df["value_to_sort"] = df.apply(
            lambda row: row["nums_cr"][0] * 10000 + row["line_order"], axis="columns"
        )
        df.sort_values(by="value_to_sort", inplace=True)

        # drop columns
        df.drop(columns=["title", "line_order", "value_to_sort"], inplace=True)

        # fields to string
        df["dates"] = df["dates"].apply(
            lambda dates: ", ".join(date.strftime("%d-%m-%Y") for date in dates)
        )
        for col in ["nums_cr", "pages"]:
            df[col] = df[col].apply(lambda lst: ", ".join(str(e) for e in lst))

        # columns
        new_columns = columns_final_name.copy()
        new_columns[0] += f" ({len(df)} au total)"
        df.rename(columns=dict(zip(columns, new_columns)), inplace=True)

        # docx
        doc.add_table(
            df,
            color_header=LIGHT_BLUE,
            color_cells=LIGHT_GREY,
            column_widths=[4, 1, 0.8, 0.8],
        )

        doc.add_newline()

    # Enregistrement
    doc.save(path_docx)

    print(f"Docx '{path_docx}' saved.")


def extract_infos_and_write_doc(path_docx_to_write: Path, filters: Filters) -> None:

    filters_args = convert_filters_to_args(filters)

    # 1. get infos
    df_compressed = load_df_compressed()
    if df_compressed is not None:
        df_compressed = filter_compressed(df_compressed, **filters_args)
    else:  # need to compute
        _, _, df_compressed = extract_infos_saint_amand(
            projects_to_extract=filters.projects, **filters_args
        )

    # 2. write

    # rename columns
    df_compressed.rename(columns={"pages_table_start": "pages"}, inplace=True)

    write_chrono(df_compressed, path_docx_to_write, filters_args["cr_num_bounds"])


if __name__ == "__main__":

    filters = Filters(
        projects=["Lot 2 "],
        date_min=None,
        date_max=None,
        cr_num_min=1,
        cr_num_max=10,
    )

    extract_infos_and_write_doc(PATH_TMP / "test.docx", filters=filters)
