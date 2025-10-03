from pathlib import Path

import cache as cache_module
import docs as docs_module
import models as models_module
import tmp as tmp_module

try:
    PATH_DOCS = Path(docs_module.__file__).parent
    PATH_CACHE = Path(cache_module.__file__).parent
    PATH_TMP = Path(tmp_module.__file__).parent
    PATH_MODELS = Path(models_module.__file__).parent
except:
    PATH_DOCS = Path("docs/")
    PATH_CACHE = Path("cache/")
    PATH_TMP = Path("tmp/")
    PATH_MODELS = Path("models/")

# docs
PATH_SAINT_AMAND_INTEGRAL = PATH_DOCS / "intégrale CR chantier Saint Amand.pdf"
PATH_MAUBEUGE_INTEGRAL = PATH_DOCS / "intégrale CR chantier Maubeuge.pdf"
PATH_AUBY_INTEGRAL = PATH_DOCS / "intégrale CR auby compilés.pdf"

# models
PATH_MODEL_MINI = PATH_MODELS / "all-MiniLM-L6-v2"
