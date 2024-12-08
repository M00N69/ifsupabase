from openpyxl import load_workbook
import pandas as pd
from datetime import datetime


def sanitize_value(value):
    """Clean and convert values to avoid errors."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        value = value.strip()
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
        return value
    if value in [None, "", " "]:
        return None
    return str(value)


def extract_metadata(uploaded_file):
    """Extract metadata from the Excel file."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        metadata = {
            "nom": sanitize_value(ws.cell(4, 3).value),
            "coid": sanitize_value(ws.cell(5, 3).value),
            "referentiel": sanitize_value(ws.cell(7, 3).value),
            "type_audit": sanitize_value(ws.cell(8, 3).value),
            "date_audit": sanitize_value(ws.cell(9, 3).value),
        }
        if not all(metadata.values()):
            raise ValueError("Les métadonnées sont incomplètes ou invalides.")
        return metadata
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction des métadonnées : {e}")


def extract_nonconformities(uploaded_file):
    """Extract non-conformities from the table."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Row 12
        data = []

        for row in ws.iter_rows(min_row=14, values_only=True):
            if any(row):
                data.append([sanitize_value(cell) for cell in row])

        df = pd.DataFrame(data, columns=headers)
        column_mapping = {
            "requirementNo": "requirementno",
            "requirementText": "requirementtext",
            "requirementScore": "requirementscore",
            "requirementExplanation": "requirementexplanation",
            "correctionDescription": "correctiondescription",
            "correctionResponsibility": "correctionresponsibility",
            "correctionDueDate": "correctionduedate",
            "correctionStatus": "correctionstatus",
            "correctionEvidence": "correctionevidence",
            "correctiveActionDescription": "correctiveactiondescription",
            "correctiveActionResponsibility": "correctiveactionresponsibility",
            "correctiveActionDueDate": "correctiveactionduedate",
            "correctiveActionStatus": "correctiveactionstatus",
            "releaseResponsibility": "releaseresponsibility",
            "releaseDate": "releasedate",
        }
        return df.rename(columns=column_mapping)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction des non-conformités : {e}")
