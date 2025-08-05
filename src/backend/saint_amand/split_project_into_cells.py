import datetime
import re
from typing import List, Optional, Tuple

import pandas as pd
from tqdm import tqdm

from backend.saint_amand.projects import Projects
from backend.saint_amand.split_page_into_projects import (
    TABLES_HEADER_MAUBEUGE,
    is_start_line_table_maubeuge,
)


def _extract_header_saint_amand(lines: List[str]) -> Tuple[str, str, List[str]]:
    title = lines[0].strip(" ")
    company = lines[1]

    rest = lines[2:]

    return title, company, rest


def _extract_header_maubeuge(lines: List[str]) -> Tuple[str, str, List[str]]:
    title = None
    for header in TABLES_HEADER_MAUBEUGE.keys():
        if header and lines[0].startswith(header):
            title = header
            break

    if title is None:
        print(lines)
        raise ValueError("toto")

    rest = lines[1:]
    rest_first_line = lines[0][len(title) :].strip(" ")
    if rest_first_line:
        rest = [rest_first_line] + rest

    return title, None, rest


def _extract_date_saint_amand(line: str) -> Optional[Tuple[datetime.datetime, str]]:
    groups = re.match(pattern=r"(\d\d/\d\d/\d\d)( |$)", string=line)
    if len(groups) == 0:
        return None

    assert len(groups) == 1
    date_str = line[:8]
    date = datetime.date(
        year=2000 + int(date_str[-2:]),
        month=int(date_str[3:5]),
        day=int(date_str[:2]),
    )
    return date, line[8:]


def _extract_date_maubeuge(line: str) -> Optional[Tuple[datetime.datetime, str]]:
    groups = re.match(pattern=r"- (\d\d/\d\d/\d\d) :", string=line)

    if groups is None:
        return None

    groups = groups.groups()
    assert len(groups) == 1
    date_str = groups[0][:8]
    date = datetime.date(
        year=2000 + int(date_str[-2:]),
        month=int(date_str[3:5]),
        day=int(date_str[:2]),
    )
    return date, line[12:]


def _extract_cells_from_raw_text_table(
    num_cr: int,
    page_table_start: int,
    page_table_end: int,
    text_table: str,
    project: Projects,
) -> List[dict]:

    # split the lines
    lines = text_table.split("\n")

    # extract headers
    title, company, rest = {
        Projects.SAINT_AMAND: _extract_header_saint_amand,
        Projects.MAUBEUGE: _extract_header_maubeuge,
    }[project](lines)
    extract_date = {
        Projects.SAINT_AMAND: _extract_date_saint_amand,
        Projects.MAUBEUGE: _extract_date_maubeuge,
    }[project]

    # init vars
    cells: List[Tuple[str, str, int]] = []
    buffer = ""
    date = None

    # go through cells line
    for line_order, line in enumerate(rest):
        if line.strip(" ") == "":  # two following newlines --> two differents cells
            # store the cell
            cells.append((date, buffer, line_order))
            # reset buffer
            buffer = ""

        elif (
            res_extraction_date := extract_date(line)
        ) is not None:  # match a date -> end cell and start of a new one

            new_date, rest_line = res_extraction_date

            # store the cell
            cells.append((date, buffer, line_order))

            # update date
            date = new_date

            # extract the cell
            text_cell = rest_line.strip(" ")

            # store in the buffer
            buffer = text_cell

        else:  # newline without date but with text --> no new cell

            # separe lines with a newline
            if len(buffer) > 0 and buffer.strip(" ") != "":
                buffer += "\n"

            buffer += line

    cells.append((date, buffer, line_order))

    # remove empty cells
    cells = [
        (date, text, line_order)
        for date, text, line_order in cells
        if text.strip(" ") != ""
    ]

    return [
        {
            "num_cr": num_cr,
            "page_table_start": page_table_start,
            "page_table_end": page_table_end,
            "title": title,
            "company": company,
            "date": date,
            "cell": cell,
            "line_order": line_order,
        }
        for date, cell, line_order in cells
    ]


def _preprocess_table(df_row_tables: pd.DataFrame) -> pd.DataFrame:

    data = []

    titles = []

    for _, table in df_row_tables.iterrows():

        lines = table["text_table"].split("\n")

        titles.extend(
            [
                sub_line.strip(" ")
                for line in lines
                if is_start_line_table_maubeuge(line)
                for sub_line in line.split("/")
                if is_start_line_table_maubeuge(sub_line)
            ]
        )
        titles = list(set(titles))

        others = [
            line_strip
            for line in lines
            if not is_start_line_table_maubeuge(line)
            if (line_strip := line.strip(" \n\t"))
        ]

        if len(others) == 0:
            # merge
            continue

        for title in titles:
            table_copy = table.copy()
            table_copy["text_table"] = title + " \n" + "\n".join(others)
            data.append(table_copy)

            # reset titles
            titles = []

    return pd.DataFrame(data)


def split_projects_into_cells(
    df_row_tables: pd.DataFrame, project: Projects
) -> pd.DataFrame:

    # preprocess tables
    df_row_tables = {
        Projects.SAINT_AMAND: lambda x: x,
        Projects.MAUBEUGE: _preprocess_table,
    }[project](df_row_tables)

    print(df_row_tables)

    for _, table in df_row_tables.iterrows():
        text_table = table["text_table"]
        if not is_start_line_table_maubeuge(text_table):
            print(table["page_table_start"])
            print(text_table.split("\n")[0])
            print("--")

    data = []

    # process table by table
    for _, table in tqdm(
        df_row_tables.iterrows(),
        total=len(df_row_tables),
        desc="Split projects into cells",
    ):
        e = _extract_cells_from_raw_text_table(**table, project=project)
        data.extend(e)

    df = pd.DataFrame(data)
    return df
