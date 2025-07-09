import Levenshtein
import networkx as nx
import numpy as np
import pandas as pd

DISTANCE_STRING_MAX_GROUP = 5


def custom_agg(series: pd.Series):

    if isinstance(series.iloc[0], str) or isinstance(series.iloc[0], np.int64):
        return series.iloc[0]

    if isinstance(series.iloc[0], np.ndarray):
        return sum([e.tolist() for e in series], [])

    raise Exception(f"Not handled (type:{type(series.iloc[0])})")


def compress_cells(project_title: str, df_tables: pd.DataFrame) -> pd.DataFrame:

    # 1. simple group by cell string
    df_grouped = (
        df_tables.groupby("cell")
        .aggregate({"date": "unique", "num_cr": "unique", "page_table_start": "unique"})
        .reset_index()
    )

    # 2. compute levenshtein distance for all combinations
    distances = []
    for idx1, cell1 in enumerate(df_grouped["cell"]):
        for idx2, cell2 in enumerate(
            df_grouped["cell"].iloc[idx1 + 1 :], start=idx1 + 1
        ):
            score = Levenshtein.distance(cell1, cell2)
            distances.append({"idx1": idx1, "idx2": idx2, "dst": score})
    df_distances = pd.DataFrame(distances)

    # 3. make groups of cells to merged with the Graph connected components algorithm

    # keep only the links between near strings
    df_distances_filtred = df_distances[
        df_distances["dst"] <= DISTANCE_STRING_MAX_GROUP
    ]

    # build graph
    G = nx.from_edgelist(
        edgelist=zip(df_distances_filtred["idx1"], df_distances_filtred["idx2"])
    )

    # add those that are not in the levenshtein distance
    for node in range(len(df_grouped)):
        if node not in G.nodes:
            G.add_node(node)

    groups_to_merge = list(nx.connected_components(G))

    # store the info of group in the dataframe
    df_grouped["group"] = None
    for id_group, group in enumerate(groups_to_merge):
        df_grouped.loc[list(group), "group"] = id_group

    # 4. group and apply aggregation
    df_compressed_info = df_grouped.groupby("group").agg(custom_agg)

    # 5. clean and cheks

    # erase index group
    df_compressed_info.index = range(len(df_compressed_info))

    # rename
    df_compressed_info.rename(
        columns={
            "date": "dates",
            "num_cr": "nums_cr",
            "page_table_start": "pages_table_start",
        },
        inplace=True,
    )

    # remove duplicated dates
    df_compressed_info["dates"] = df_compressed_info["dates"].apply(
        lambda dates: np.unique(dates)
    )

    # add title
    df_compressed_info["title"] = project_title

    # 6. return
    return df_compressed_info
