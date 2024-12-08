import pandas as pd
from openpyxl import load_workbook

def extract_metadata(uploaded_file):
    """Extrait les métadonnées depuis le fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        metadata = {
            "nom": ws.cell(4, 3).value.strip(),
            "coid": ws.cell(5, 3).value.strip(),
            "referentiel": ws.cell(7, 3).value.strip(),
            "type_audit": ws.cell(8, 3).value.strip(),
            "date_audit": ws.cell(9, 3).value.strip(),
        }
        return metadata
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction des métadonnées : {e}")

def extract_nonconformities(uploaded_file):
    """Extrait les non-conformités depuis le fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        headers = [cell.value.strip() for cell in ws[12]]  # Row 12 as headers
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):
            if any(row):  # Ignore empty rows
                data.append(row)
        df = pd.DataFrame(data, columns=headers)
        df = df.rename(columns={
            "requirementNo": "requirementno",
            "requirementText": "requirementtext",
            "requirementScore": "requirementscore",
            "requirementExplanation": "requirementexplanation",
            "correctionDescription": "correctiondescription",
            "correctionResponsibility": "correctionresponsibility",
            "correctionDueDate": "correctionduedate",
            "correctionStatus": "correctionstatus",
            "releaseResponsibility": "releaseresponsibility",
            "releaseDate": "releasedate",
        })
        return df
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction des non-conformités : {e}")
