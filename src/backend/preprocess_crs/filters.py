import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List

from helper import cache


@dataclass
class Filters:
    projects: List[str]
    date_min: datetime
    date_max: datetime
    cr_num_min: int
    cr_num_max: int

    def save(self, label: str) -> None:
        cache.save(f"filter_bounds_{label}.json", obj=asdict(self))

    @staticmethod
    def load(label: str) -> "Filters":
        params = cache.load(f"filter_bounds_{label}.json")
        return Filters(**params)
