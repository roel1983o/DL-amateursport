import json, re
import pandas as pd

NB_PATH = "app/notebooks/DL_amateursport_overig.ipynb"

def _bootstrap_overig_funcs():
    with open(NB_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)
    code = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            # skip shell-installs and any final upload/download compose part
            if "uploaded = files.upload()" in src or "out_name" in src:
                break
            # strip explicit Google Colab import if present
            src = src.replace("from google.colab import files", "")
            code.append(src)
    ns = {}
    exec("\n\n".join(code), ns, ns)
    # Required functions coming from the notebook:
    required = ["convert_sheet1_blocks","iter_sheet2_blocks","render_table_block","to_render_blocks","suppress_redundant_sportheads"]
    for r in required:
        if r not in ns:
            raise RuntimeError(f"Kon {r} niet vinden in overig-notebook.")
    return ns

_FUNCS = None

def export_overig_from_xlsx_bytes(xlsx_bytes: bytes) -> str:
    global _FUNCS
    if _FUNCS is None:
        _FUNCS = _bootstrap_overig_funcs()
    xls = pd.ExcelFile(xlsx_bytes)
    sheet1 = pd.read_excel(xls, sheet_name=xls.sheet_names[0], dtype=str)
    sheet2 = pd.read_excel(xls, sheet_name=xls.sheet_names[1], dtype=str)

    blocks = _FUNCS["to_render_blocks"](sheet1, sheet2)
    blocks = _FUNCS["suppress_redundant_sportheads"](blocks)

    lines = ["<body>"]
    for bl in blocks:
        lines += bl["render_lines"]
    lines.append("</body>")
    output_text = "\n".join(lines)

    # Post-processing borrowed from the notebook
    output_text = re.sub(r'</howto_facts><EP>\s*<subhead>', r'</howto_facts><EP,1>\n<subhead>', output_text)
    return output_text
