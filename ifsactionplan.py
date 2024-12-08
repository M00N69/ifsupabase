from openpyxl import load_workbook

def inspect_excel(file_path):
    """Inspecter le contenu brut du fichier Excel pour localiser les métadonnées."""
    wb = load_workbook(file_path)
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        print(row)  # Afficher chaque ligne pour voir toutes les valeurs brutes
