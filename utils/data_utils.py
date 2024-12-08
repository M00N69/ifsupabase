from openpyxl import load_workbook
import pandas as pd

def sanitize_value(value):
    """Clean and convert values to avoid errors."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        value = value.strip()
    if value in [None, "", " "]:
        return None
    return value

def extract_metadata(uploaded_file):
    """Extract metadata from the audit."""
    wb = load_workbook(uploaded_file, data_only=True)
    ws = wb.active
    return {
        "nom": sanitize_value(ws.cell(4, 3).value),
        "coid": sanitize_value(ws.cell(5, 3).value),
        "referentiel": sanitize_value(ws.cell(7, 3).value),
        "type_audit": sanitize_value(ws.cell(8, 3).value),
        "date_audit": sanitize_value(ws.cell(9, 3).value),
    }

def extract_nonconformities(uploaded_file):
    """Extract non-conformities from the table."""
    wb = load_workbook(uploaded_file, data_only=True)
    ws = wb.active
    headers = [sanitize_value(cell.value) for cell in ws[12]]
    data = [
        [sanitize_value(cell) for cell in row]
        for row in ws.iter_rows(min_row=14, values_only=True)
        if any(row)
    ]
    df = pd.DataFrame(data, columns=headers)
    column_mapping = {
        "requirementNo": "requirementno",
        "requirementText": "requirementtext",
        "requirementScore": "requirementscore",
        "requirementExplanation": "requirementexplanation",
        # Add other mappings...
    }
    return df.rename(columns=column_mapping)
