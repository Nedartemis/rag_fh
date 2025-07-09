from functools import reduce
from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd
from tqdm import tqdm

from backend.read_pdf import read_pdf
from backend.saint_amand.compress_cells import compress_cells
from backend.saint_amand.compute_cr_page_number import compute_cr_page_numbers
from backend.saint_amand.split_page_into_projects import split_pages_into_projects
from backend.saint_amand.split_project_into_cells import split_projects_into_cells
from vars import PATH_DOCS


def extract_infos_saint_amand(
    path_pdf: Path,
    projects_to_extract: Optional[Union[str, List[str]]],
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[pd.DataFrame]]:

    # 1. read
    pages = read_pdf(path_pdf)

    # 2. cr
    df_cr = compute_cr_page_numbers(pages)

    # filter
    if cr_num_bounds:
        df_cr = df_cr[
            (df_cr["num_cr"] >= cr_num_bounds[0])
            & (df_cr["num_cr"] <= cr_num_bounds[1])
        ]

    # 3. row tables
    df_row_tables = split_pages_into_projects(pages, df_cr)

    # 4. tables
    df_tables = split_projects_into_cells(df_row_tables)

    # filter
    if not isinstance(projects_to_extract, list):
        projects_to_extract = [projects_to_extract]

    project_titles_to_extract = [
        title
        for title in df_tables["title"].unique()
        for to_extract in projects_to_extract
        if to_extract in title
    ]
    df_tables = df_tables[df_tables["title"].isin(project_titles_to_extract)]

    # error handling
    if len(projects_to_extract) != len(df_tables["title"].unique()):
        raise RuntimeError(
            f"{projects_to_extract} ; {df_tables['title'].unique().tolist()}"
        )

    # 5. compress

    dfs_compressed: List[pd.DataFrame] = []
    for project_title in tqdm(df_tables["title"].unique(), desc="Compress infos"):
        df = compress_cells(
            project_title, df_tables[df_tables["title"].str.contains(project_title)]
        )
        dfs_compressed.append(df)

    # 6. return
    return df_cr, df_tables, dfs_compressed


if __name__ == "__main__":
    extract_infos_saint_amand(
        PATH_DOCS / "intégrale CR chantier Saint Amand.pdf", "Lot 2 "
    )
