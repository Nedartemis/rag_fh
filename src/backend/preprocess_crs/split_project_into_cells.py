import datetime
import re
from typing import List, Optional, Tuple

import pandas as pd
from tqdm import tqdm

from backend.preprocess_crs.projects import Projects
from backend.preprocess_crs.split_page_into_projects import (
    TABLES_HEADER_MAUBEUGE,
    is_start_line_table_auby,
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
    if groups is None:
        return None

    groups = groups.groups()
    assert not isinstance(groups, list) or len(groups) == 1

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


def _preprocess_table_maubeuge(df_row_tables: pd.DataFrame) -> pd.DataFrame:

    data = []

    titles = []

    for _, table in df_row_tables.iterrows():

        lines = table["text_table"].split("\n")

        # multiple titles
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

        # all the line that does not begin by the title of a project and is not empty
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


MONKEY_FIXES_LIST = [
    [("TCE", 2), ("DRD", 1), ("BC", 2), ("TCE", -1)],
    [("CERGNUL", 2), ("TCE", -1)],
    [("TCE", 3), ("TCE", -1)],
    [("BC", 1), ("BC", 1), ("TCE", -1)],
]


def _split_projects_into_cells_auby(
    df_row_tables: pd.DataFrame,
) -> pd.DataFrame:

    data = []

    idx = 0
    while idx < len(df_row_tables):

        # print("\n\n\n")

        # list of : multiples titles with the number of cell
        titles: List[Tuple[List[str], int]] = []
        s = df_row_tables.iloc[idx]
        num_cr = s["num_cr"]
        page_table_start = s["page_table_start"]

        # print(idx, num_cr, page_table_start)

        # go until there is no more titles
        while True:
            text: str = df_row_tables["text_table"].iloc[idx]
            lines = [
                line_strip
                for line in text.split("\n")
                if (line_strip := line.strip(" "))
            ]

            other = [line for line in lines if not is_start_line_table_auby(line)]
            assert len(other) == len(lines) - 1

            titles.append([lines[0], (text.count("\n") + 1) if len(lines) == 1 else -1])

            if len(other) > 0:
                # text
                break

            idx += 1

        if len(titles) == 0:
            idx += 1
            continue

        # dont manage "AVANCEMENT – PLANIFICATION"
        if any("AVANCEMENT – PLANIFICATION" in text for text in other):
            # skip the end of the cr
            while (
                idx < len(df_row_tables) and num_cr == df_row_tables["num_cr"].iloc[idx]
            ):
                idx += 1
            continue

        # fusion titles on multiple lines
        old_titles = titles
        titles = []
        add_with_previous = False
        for title, e in old_titles:
            if add_with_previous:
                t, nb = titles[-1]
                titles[-1] = (t + title, (nb + e) if e != -1 else -1)
            else:
                titles.append((title, e))
            add_with_previous = title.endswith("/")

        # print(titles)
        # print(other)

        page_table_end = df_row_tables.iloc[idx]["page_table_start"]

        # remove first lines without '-'
        idx_cut = 0
        while idx_cut < len(other) and not other[idx_cut].startswith("-"):
            idx_cut += 1
        other = other[idx_cut:]

        # build other with the number of line of each text
        texts_nb: List[Tuple[str, int]] = []
        buffer = ""
        nb = 0
        for text in other:
            if text.startswith("-"):
                texts_nb.append((buffer, nb))
                buffer = ""
                nb = 0

            buffer += " " + text
            nb += 1

        texts_nb = texts_nb[1:] + [(buffer, nb)]

        # print()
        # print(texts_nb)

        # duplicate some titles
        new_titles = []
        for (title, nb_title), (text, nb_text) in zip(titles, texts_nb):
            if nb_title == nb_text or nb_title == -1 or title == "MQB/EAS/DEVRED":
                new_titles.append((title, nb_title))
            elif nb_title > nb_text:
                new_titles += [(title, 1)] * (nb_title - nb_text + 1)
        titles = new_titles

        # print()
        # print(titles)

        # check consistency
        if not any(
            all(t1 == t2 and n1 == n2 for (t1, n1), (t2, n2) in zip(titles, lst))
            for lst in MONKEY_FIXES_LIST
        ):
            for (title, nb_title), (text, nb_text) in zip(titles, texts_nb):
                assert (
                    nb_title == nb_text
                    or nb_title == -1
                    or title == "MQB/EAS/DEVRED"
                    or title == "DR/BERIM/BC/MQB"
                ), f"{title} | {text}"

        # extend list titles
        assert len(titles) <= len(texts_nb)
        if len(titles) == 0:
            idx += 1
            continue
        titles += [titles[0]] * (len(other) - len(titles))

        # add cells
        for idx_text, ((title, _), (text, _)) in enumerate(zip(titles, texts_nb)):

            res = _extract_date_maubeuge(text[1:])
            if res is None:
                continue
            date, text = res

            for sub_title in title.split("/"):

                data.append(
                    {
                        "num_cr": num_cr,
                        "page_table_start": page_table_start,
                        "page_table_end": page_table_end,
                        "title": sub_title,
                        "date": date,
                        "cell": text,
                        "line_order": idx_text,
                    }
                )

        # print(pd.DataFrame(data))

        idx += 1

    df = pd.DataFrame(data)
    # print(df)

    return df


def split_projects_into_cells(
    df_row_tables: pd.DataFrame, project: Projects
) -> pd.DataFrame:

    if project in [Projects.SAINT_AMAND, Projects.MAUBEUGE]:
        # preprocess tables
        df_row_tables = {
            Projects.SAINT_AMAND: lambda x: x,
            Projects.MAUBEUGE: _preprocess_table_maubeuge,
        }[project](df_row_tables)

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
    elif project == Projects.AUBY:
        return _split_projects_into_cells_auby(df_row_tables)
    else:
        raise ValueError(f"Project '{project}' not handled.")
