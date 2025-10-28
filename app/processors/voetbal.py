import re
import pandas as pd
from io import BytesIO
from types import SimpleNamespace

# We dynamically read the user's original Colab notebook and execute the
# *function definitions only* (we skip the upload / download parts).
# Expected to find a `build_output(filebytes: bytes) -> str` function in it.
NB_PATH = "app/notebooks/DL_amateursport_voetbal.ipynb"

def _load_build_output_from_notebook():
    import json
    with open(NB_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)
    code = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            # skip shell-installs and any upload/download code
            if "files.upload(" in src or "files.download(" in src:
                break
            code.append(src)
    ns = {}
    exec("\n\n".join(code), ns, ns)
    if "build_output" not in ns:
        raise RuntimeError("Kon functie build_output() niet vinden in voetbal-notebook.")
    return ns["build_output"]

_BUILDER = None

def export_voetbal_from_xlsx_bytes(xlsx_bytes: bytes) -> str:
    global _BUILDER
    if _BUILDER is None:
        _BUILDER = _load_build_output_from_notebook()
    return _BUILDER(xlsx_bytes)
