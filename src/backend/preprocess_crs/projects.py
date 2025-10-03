from datetime import datetime
from enum import Enum

from backend.preprocess_crs.filters import Filters


class Projects(Enum):
    SAINT_AMAND = 0
    MAUBEUGE = 1
    AUBY = 2

    def get_label(self) -> str:
        return str(self.name).replace("_", "-").lower()

    def load_bounds(self) -> Filters:
        return Filters.load(self.get_label())
