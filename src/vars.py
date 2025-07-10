from pathlib import Path

import cache as cache_module
import docs as docs_module
import tmp as tmp_module

PATH_DOCS = Path(docs_module.__file__).parent
PATH_CACHE = Path(cache_module.__file__).parent
PATH_TMP = Path(tmp_module.__file__).parent

PATH_SAINT_AMAND_INTEGRAL = PATH_DOCS / "intégrale CR chantier Saint Amand.pdf"
