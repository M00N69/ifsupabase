import pandas as pd
from openpyxl import load_workbook


def sanitize_value(value):
    """Nettoie et formate les valeurs pour éviter les erreurs."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    if value in [None, "", " "]:
        return None
    return value


def extract_metadata(uploaded_file):
    """Extrait les métadonnées depuis le fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        metadata = {
            "nom": sanitize_value(ws.cell(4, 3).value),  # Ligne 4, Colonne C
            "coid": sanitize_value(ws.cell(5, 3).value),
            "referentiel": sanitize_value(ws.cell(7, 3).value),
            "type_audit": sanitize_value(ws.cell(8, 3).value),
            "date_audit": sanitize_value(ws.cell(9, 3).value),
        }

        # Validation des métadonnées
        if not metadata["coid"] or not metadata["nom"]:
            raise ValueError("Les champs obligatoires dans les métadonnées sont manquants.")

        return metadata
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction des métadonnées : {e}")


def extract_nonconformities(uploaded_file):
    """Extrait les non-conformités depuis le fichier Excel."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Ligne 12 comme en-tête
        data = [
            [sanitize_value(cell) for cell in row]
            for row in ws.iter_rows(min_row=14, values_only=True)
            if any(row)
        ]

        df = pd.DataFrame(data, columns=headers)

        # Mapping des colonnes pour la base de données
        column_mapping = {
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
        }

        df.rename(columns=column_mapping, inplace=True)

        if df.empty:
            raise ValueError("Aucune non-conformité trouvée dans le fichier Excel.")

        return df
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction des non-conformités : {e}")
