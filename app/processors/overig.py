import json, re, inspect
import pandas as pd
import io

NB_PATH = "app/notebooks/DL_amateursport_overig.ipynb"

def _bootstrap_overig_funcs():
    with open(NB_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)
    code = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        # Colab-artefacts overslaan
        src = src.replace("from google.colab import files", "")
        if "files.upload(" in src or "files.download(" in src:
            continue
        code.append(src)
    ns = {}
    exec("\n\n".join(code), ns, ns)
    return ns

_FUNCS = None

def _found_callables(ns):
    return sorted([k for k,v in ns.items() if callable(v)])

def export_overig_from_xlsx_bytes(xlsx_bytes: bytes) -> str:
    global _FUNCS
    if _FUNCS is None:
        _FUNCS = _bootstrap_overig_funcs()

    # 1) Probeer directe entrypoints uit de notebook
    entry_names = ["build_output_overig", "build_output", "export_overig"]
    for name in entry_names:
        if name in _FUNCS and callable(_FUNCS[name]):
            func = _FUNCS[name]
            sig = inspect.signature(func)
            try:
                if len(sig.parameters) <= 1:
                    # verwacht bytes of pad
                    return func(xlsx_bytes)
                else:
                    # maak sheet1, sheet2 en geef die door
                    bio = io.BytesIO(xlsx_bytes)
                    xls = pd.ExcelFile(bio)
                    sheet1 = pd.read_excel(xls, sheet_name=xls.sheet_names[0], dtype=str)
                    sheet2 = pd.read_excel(xls, sheet_name=xls.sheet_names[1], dtype=str)
                    return func(sheet1, sheet2)
            except TypeError:
                # fallback naar (sheet1, sheet2) als bytes niet werkt
                bio = io.BytesIO(xlsx_bytes)
                xls = pd.ExcelFile(bio)
                sheet1 = pd.read_excel(xls, sheet_name=xls.sheet_names[0], dtype=str)
                sheet2 = pd.read_excel(xls, sheet_name=xls.sheet_names[1], dtype=str)
                return func(sheet1, sheet2)

    # 2) Fallback: bestaande bouwstenen (oude structuur)
    required = ["to_render_blocks","suppress_redundant_sportheads"]
    if all(r in _FUNCS for r in required):
        bio = io.BytesIO(xlsx_bytes)
        xls = pd.ExcelFile(bio)
        sheet1 = pd.read_excel(xls, sheet_name=xls.sheet_names[0], dtype=str)
        sheet2 = pd.read_excel(xls, sheet_name=xls.sheet_names[1], dtype=str)

        blocks = _FUNCS["to_render_blocks"](sheet1, sheet2)
        blocks = _FUNCS["suppress_redundant_sportheads"](blocks)

        lines = ["<body>"]
        for bl in blocks:
            lines += bl["render_lines"]
        lines.append("</body>")
        output_text = "\n".join(lines)
        output_text = re.sub(r'</howto_facts><EP>\s*<subhead>',
                             r'</howto_facts><EP,1>\n<subhead>',
                             output_text)
        return output_text

    # 3) Niets gevonden: meld helder wat er wél in de notebook zit
    funcs = ", ".join(_found_callables(_FUNCS)) or "(geen functies gevonden)"
    raise RuntimeError(
        "Kon geen bekende exportfunctie vinden. "
        "Probeer in je notebook een van deze functies te definiëren: "
        "build_output_overig(xlsx_bytes), build_output(xlsx_bytes) of export_overig(sheet1, sheet2). "
        f"Gevonden functies: {funcs}"
    )
