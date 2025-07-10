import json
import os
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from vars import PATH_CACHE


def check_filename(filename: str) -> None:
    if "/" in filename:
        raise ValueError(f"Must be a simple filename, not a path. Got {filename}")


def load(filename: str) -> Optional[Any]:

    # check_filename(filename)

    path: Path = PATH_CACHE / filename
    if not path.exists():
        return None

    if path.suffix == "":  # folder
        obj = []
        for sub_filename in os.listdir(path):
            e = load(path / sub_filename)
            obj.append(e)
    elif path.suffix == ".json":
        with open(path, mode="r") as fr:
            obj = json.load(fr)
    elif path.suffix == ".csv":
        obj = pd.read_csv(path)
    else:
        raise ValueError(f"Extension '{path.suffix}' not handled")

    return obj


def save(filename: str, obj: Any, ext: Optional[str] = None) -> None:

    # check_filename(filename)

    path = PATH_CACHE / filename

    if path.suffix == "":  # folder
        if not isinstance(obj, list):
            raise ValueError(f"Folder is only handled with a list, got {type(obj)}")
        if ext is None:
            raise ValueError("To save a folder, the extension precision is mandatory.")

        os.makedirs(path, exist_ok=True)
        for idx, sub_obj in enumerate(obj):
            save(Path(filename) / (str(idx) + ext), sub_obj)
    elif path.suffix == ".json":
        with open(path, mode="w") as fw:
            json.dump(obj, fw)
    elif path.suffix == ".csv":
        if not isinstance(obj, pd.DataFrame):
            raise ValueError(
                f"Extension '.csv' is only handled with a dataframe, got {type(obj)}"
            )
        obj.to_csv(path, index=False)
    else:
        raise ValueError(f"Extension '{path.suffix}' not handled")
