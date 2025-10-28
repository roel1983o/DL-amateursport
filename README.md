# DL regiosport codefixer

FastAPI-webapp die twee bestaande Colab-notebooks gebruikt om Excel-uitslagen om te zetten naar CUE-tekstbestanden.
Kopieer deze repo naar GitHub en deploy op Render.com (of lokaal met Docker).

## Snel starten (Render)

1. Maak een nieuwe **Public** GitHub-repo en upload alle bestanden uit deze map.
2. Ga naar **Render.com → New → Web Service** en kies je repo.
3. Render herkent `render.yaml`. Controleer:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Deploy. Na ~1 minuut staat de webapp live.

## Lokaal draaien

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open daarna http://127.0.0.1:8000/

## Werking

- **Voetbal**: we lezen je originele notebook en voeren alleen de *functie-definities* uit (tot aan het upload/download-gedeelte). We verwachten een functie `build_output(filebytes: bytes) -> str`. De app roept die aan met de geüploade `.xlsx` en geeft het `.txt` resultaat terug.
- **Overig**: we laden de functies uit je notebook (`convert_sheet1_blocks`, `iter_sheet2_blocks`, `render_table_block`, `to_render_blocks`, `suppress_redundant_sportheads`) en bouwen het tekstbestand zoals in je notebook (incl. de EP→EP,1 nabehandeling).

De originele notebooks staan in `app/notebooks/` en blijven leidend. Als je die bijwerkt, hoeft de app-code niet aangepast te worden.

## Bestanden

```
app/
  main.py                 # FastAPI app + routes
  templates/index.html    # UI (zie ontwerp)
  static/style.css        # eenvoudige styling
  processors/             # notebook-wrappers
  notebooks/              # je originele .ipynb-bestanden
samples/
  Invulbestand_amateursport_voetbal.xlsx
  Invulbestand_amateursport_overig.xlsx
requirements.txt
render.yaml
Dockerfile (optioneel)
```

## Tips

- Houd de kolomnamen/werkbladen in de Excel-templates gelijk aan wat de notebooks verwachten.
- Bij fouten zie je in Render de logs. Vaak is een mismatch in kolomnamen of een lege sheet de oorzaak.
- Wil je de HTML aanpassen? Pas `app/templates/index.html` en `app/static/style.css` aan.
