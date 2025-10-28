import re
import pandas as pd
from io import BytesIO
from types import SimpleNamespace

# We dynamically read the user's original Colab notebook and execute the
# *function definitions only* (we skip the upload / download parts).
# Expected to find a `build_output(filebytes: bytes) -> str` function in it.
NB_PATH = "app/notebooks/DL_amateursport_voetbal.ipynb"

def _load_build_output_from_notebook():
    import json, re
    with open(NB_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    code_cells = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        # Colab upload/download en imports weghalen, maar niet stoppen
        src = src.replace("from google.colab import files", "")
        if "files.upload(" in src or "files.download(" in src:
            continue
        code_cells.append(src)

    ns = {}
    exec("\n\n".join(code_cells), ns, ns)

    # We verwachten deze helper in je notebook:
    if "build_output" not in ns:
        # Helpvolle foutmelding met lijst van functies die wél gevonden zijn
        funcs = [k for k, v in ns.items() if callable(v)]
        raise RuntimeError(
            "Kon functie build_output(xlsx_bytes: bytes) niet vinden in voetbal-notebook. "
            f"Gevonden functies: {', '.join(funcs) or '(geen)'}"
        )
    return ns["build_output"]

_BUILDER = None

def export_voetbal_from_xlsx_bytes(xlsx_bytes: bytes) -> str:
    global _BUILDER
    if _BUILDER is None:
        _BUILDER = _load_build_output_from_notebook()
    return _BUILDER(xlsx_bytes)
