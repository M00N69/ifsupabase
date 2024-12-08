from openpyxl import load_workbook

def inspect_excel(file_path):
    """Inspecter chaque ligne et colonne du fichier Excel."""
    wb = load_workbook(file_path)
    ws = wb.active
    for row_index, row in enumerate(ws.iter_rows(values_only=True), start=1):
        print(f"Ligne {row_index}: {row}")
