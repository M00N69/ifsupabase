import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
import streamlit as st


def sanitize_value(value):
    """Nettoie et convertit les valeurs pour éviter les erreurs."""
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
        return None  # Retourne None pour les valeurs vides
    return str(value)


def extract_metadata(uploaded_file):
    """Extrait les métadonnées du fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        return {
            "nom": sanitize_value(ws.cell(4, 3).value),  # Ligne 4, Colonne C
            "coid": sanitize_value(ws.cell(5, 3).value),  # Ligne 5, Colonne C
            "referentiel": sanitize_value(ws.cell(7, 3).value),  # Ligne 7, Colonne C
            "type_audit": sanitize_value(ws.cell(8, 3).value),  # Ligne 8, Colonne C
            "date_audit": sanitize_value(ws.cell(9, 3).value),  # Ligne 9, Colonne C
        }
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None


def extract_nonconformities(uploaded_file):
    """Extrait les non-conformités du fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Ligne 12 (en-têtes)
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):  # Données à partir de la ligne 14
            if any(row):  # Ignore les lignes vides
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
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None
