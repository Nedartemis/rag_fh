import json
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from backend.preprocess_crs.compress_cells import compress_cells
from backend.preprocess_crs.compute_cr_page_number import compute_cr_page_numbers
from backend.preprocess_crs.projects import Projects
from backend.preprocess_crs.split_page_into_projects import split_pages_into_projects
from backend.preprocess_crs.split_project_into_cells import split_projects_into_cells
from backend.read_pdf import read_pdf
from frontend.filters import Filters
from helper import cache
from vars import PATH_DOCS, PATH_MAUBEUGE_INTEGRAL, PATH_SAINT_AMAND_INTEGRAL

# ----------------- Helper -----------------


def convert_filters_to_args(filters: Filters) -> dict:
    return {
        "projects_to_extract": filters.projects,
        "date_bounds": (
            (filters.date_min, filters.date_max) if filters.date_min else None
        ),
        "cr_num_bounds": (
            (filters.cr_num_min, filters.cr_num_max) if filters.cr_num_min else None
        ),
    }


# ----------------- Compute conditions -----------------

TYPE_COND = Union[bool, pd.Series]


def compute_cond_num_cr(
    df: pd.DataFrame,
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> TYPE_COND:
    if not cr_num_bounds:
        return pd.Series([True] * len(df))

    return (df["num_cr"] >= cr_num_bounds[0]) & (df["num_cr"] <= cr_num_bounds[1])


def compute_cond_projects(
    df: pd.DataFrame,
    projects_to_extract: Optional[Union[str, List[str]]],
) -> TYPE_COND:
    if not projects_to_extract:
        return pd.Series([True] * len(df))

    if isinstance(projects_to_extract, str):
        projects_to_extract = [projects_to_extract]

    project_titles_to_extract = [
        title
        for title in df["title"].unique()
        for to_extract in projects_to_extract
        if to_extract in title
    ]
    project_titles_to_extract = np.unique(project_titles_to_extract)
    return df["title"].isin(project_titles_to_extract)


def compute_cond_date(
    df: pd.DataFrame,
    date_bounds: Optional[Tuple[datetime, datetime]] = None,
) -> TYPE_COND:
    if not date_bounds:
        return pd.Series([True] * len(df))

    return (date_bounds[0].strftime("%d/%m/%Y") <= df["date"]) & (
        df["date"] <= date_bounds[1].strftime("%d/%m/%Y")
    )


# ----------------- Filters conditions -----------------


def filter_cr(
    df_cr: pd.DataFrame,
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> pd.DataFrame:
    return df_cr[compute_cond_num_cr(df_cr, cr_num_bounds)]


def filter_tables(
    df_tables: pd.DataFrame,
    projects_to_extract: Optional[Union[str, List[str]]],
    date_bounds: Optional[Tuple[datetime, datetime]] = None,
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> pd.DataFrame:

    return df_tables[
        compute_cond_projects(df_tables, projects_to_extract)
        & compute_cond_date(df_tables, date_bounds)
        & compute_cond_num_cr(df_tables, cr_num_bounds)
    ]


def filter_compressed(
    df_compressed: List[pd.DataFrame],
    projects_to_extract: Optional[Union[str, List[str]]],
    date_bounds: Optional[Tuple[datetime, datetime]] = None,
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> List[pd.DataFrame]:

    df_cond = df_compressed.copy()

    # pre-process
    df_cond["num_cr"] = df_cond["nums_cr"].apply(lambda nums: min(nums))
    df_cond["date"] = df_cond["dates"].apply(lambda dates: min(dates))

    # apply conditions
    return df_compressed[
        compute_cond_projects(df_cond, projects_to_extract)
        & compute_cond_date(df_cond, date_bounds)
        & compute_cond_num_cr(df_cond, cr_num_bounds)
    ]


# ----------------- Save -----------------


def save_infos(
    project: Projects,
    df_cr: pd.DataFrame,
    df_tables: pd.DataFrame,
    df_compressed: pd.DataFrame,
) -> None:

    label = {
        Projects.SAINT_AMAND: "saint-amand",
        Projects.MAUBEUGE: "maubeuge",
    }[project]

    cache.save(f"dfs/{label}_cr.csv", df_cr)
    cache.save(f"dfs/{label}_tables.csv", df_tables)

    # pre-process
    df_compressed = df_compressed.copy()
    df_compressed["dates"] = df_compressed["dates"].apply(
        lambda dates: [date.strftime("%d-%m-%Y") for date in dates]
    )

    cache.save(f"dfs/{label}_compressed.csv", df_compressed)

    print("DataFrames have been saved.")


# ----------------- Load -----------------


def load_df_cr(label: str) -> Optional[pd.DataFrame]:
    return cache.load(f"dfs/{label}_cr.csv")


def load_df_tables(label: str) -> Optional[pd.DataFrame]:
    return cache.load(f"dfs/{label}_tables.csv")


def load_df_compressed(label: str) -> Optional[pd.DataFrame]:
    df = cache.load(f"dfs/{label}_compressed.csv")

    # convert nums_cr and pages
    df["nums_cr"] = df["nums_cr"].apply(json.loads)
    df["pages_table_start"] = df["pages_table_start"].apply(json.loads)

    # convert dates
    convert_to_dates = lambda dates: [
        datetime.strptime(date_string, "%d-%m-%Y")
        for date_string in json.loads(dates.replace("'", '"'))
    ]
    df["dates"] = df["dates"].apply(convert_to_dates)

    return df


# ----------------- Main -----------------


def extract_infos(
    project: Projects,
    projects_to_extract: Optional[Union[str, List[str]]],
    date_bounds: Optional[Tuple[datetime, datetime]] = None,
    cr_num_bounds: Optional[Tuple[int, int]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    # 1. read
    path_pdf = {
        Projects.SAINT_AMAND: PATH_SAINT_AMAND_INTEGRAL,
        Projects.MAUBEUGE: PATH_MAUBEUGE_INTEGRAL,
    }[project]

    pages = read_pdf(path_pdf)

    # 2. cr
    df_cr = compute_cr_page_numbers(pages, project=project)

    # filter by cr numbers
    df_cr = filter_cr(df_cr, cr_num_bounds)

    # 3. row tables
    df_row_tables = split_pages_into_projects(pages, df_cr, project)

    # 4. tables
    df_tables = split_projects_into_cells(df_row_tables, project)

    # filter by project name and dates
    df_tables = filter_tables(
        df_tables, projects_to_extract=projects_to_extract, date_bounds=date_bounds
    )

    if projects_to_extract is None:
        projects_to_extract = df_tables["title"].unique()

    # error handling
    if len(projects_to_extract) != len(df_tables["title"].unique()):
        raise RuntimeError(
            f"{projects_to_extract} ; {df_tables['title'].unique().tolist()}"
        )

    df_tables = df_tables[df_tables["date"].notna()]

    # 5. compress

    dfs_compressed: List[pd.DataFrame] = []
    for project_title in tqdm(df_tables["title"].unique(), desc="Compress infos"):
        df = compress_cells(
            project_title, df_tables[df_tables["title"].str.contains(project_title)]
        )
        dfs_compressed.append(df)

    df_compressed = pd.concat(dfs_compressed, axis="index")

    # 6. return
    return df_cr, df_tables, df_compressed


if __name__ == "__main__":
    lots_name = ["Lot 2 ", "Lot 14 ", "Lot 24 "]

    project = Projects.MAUBEUGE

    df_cr, df_tables, df_compressed = extract_infos(
        project=project,
        projects_to_extract=None,
    )

    if True:
        save_infos(project, df_cr, df_tables, df_compressed)
