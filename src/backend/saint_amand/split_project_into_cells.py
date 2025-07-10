import datetime
import re
from typing import List, Tuple

import pandas as pd
from tqdm import tqdm


def _extract_cells_from_raw_text_table(
    num_cr: int, page_table_start: int, page_table_end: int, text_table: str
) -> List[dict]:

    # split the lines
    lines = text_table.split("\n")

    # save headers
    title = lines[0].strip(" ")
    company = lines[1]

    # init vars
    cells: List[Tuple[str, str, int]] = []
    buffer = ""
    date = None

    # go through cells line
    for line_order, line in enumerate(lines[2:]):
        if line.strip(" ") == "":  # two following newlines --> two differents cells
            # store the cell
            cells.append((date, buffer, line_order))
            # reset buffer
            buffer = ""

        elif re.match(
            r"\d\d/\d\d/\d\d( |$)", line
        ):  # match a date -> end cell and start of a new one

            # store the cell
            cells.append((date, buffer, line_order))

            # extract the date
            date_str = line[:8]
            date = datetime.date(
                year=2000 + int(date_str[-2:]),
                month=int(date_str[3:5]),
                day=int(date_str[:2]),
            )

            # extract the cell
            text_cell = line[8:].strip(" ")

            # store in the buffer
            buffer = text_cell
        else:  # newline without date but with text --> no new cell

            # separe lines with a newline
            if len(buffer) > 0 and buffer.strip(" ") != "":
                buffer += "\n"

            buffer += line

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


def split_projects_into_cells(df_row_tables: pd.DataFrame) -> pd.DataFrame:

    data = []

    # process table by table
    for _, table in tqdm(
        df_row_tables.iterrows(),
        total=len(df_row_tables),
        desc="Split projects into cells",
    ):
        e = _extract_cells_from_raw_text_table(**table)
        data.extend(e)

    return pd.DataFrame(data)
