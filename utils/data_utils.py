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
            # Handle date conversion
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
        return value
    if value in [None, "", " "]:
        return None  # Normalize empty values to None
    return str(value)


def extract_metadata(uploaded_file):
    """Extract metadata from the Excel file."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        return {
            "nom": sanitize_value(ws.cell(4, 3).value),  # Row 4, Column 3 (C)
            "coid": sanitize_value(ws.cell(5, 3).value),  # Row 5, Column 3 (C)
            "referentiel": sanitize_value(ws.cell(7, 3).value),  # Row 7, Column 3 (C)
            "type_audit": sanitize_value(ws.cell(8, 3).value),  # Row 8, Column 3 (C)
            "date_audit": sanitize_value(ws.cell(9, 3).value),  # Row 9, Column 3 (C)
        }
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction des métadonnées : {e}")


def extract_nonconformities(uploaded_file):
    """Extract non-conformities table from the Excel file."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active

        # Extract header row
        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Row 12
        data = []

        # Extract data rows starting at Row 14
        for row in ws.iter_rows(min_row=14, values_only=True):
            if any(row):  # Ignore empty rows
                data.append([sanitize_value(cell) for cell in row])

        # Convert to DataFrame and rename columns
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
