import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client
import pandas as pd

# Configuration de Supabase via st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fonctions utilitaires
def get_merged_cell_value(ws, row, column):
    """Obtenir la valeur d'une cellule fusionnée ou non."""
    for merged_range in ws.merged_cells.ranges:
        if (row, column) in merged_range:
            return ws.cell(merged_range.min_row, merged_range.min_col).value
    return ws.cell(row, column).value

def sanitize_value(value):
    """Nettoyer les valeurs pour éviter les erreurs."""
    if isinstance(value, tuple):
        return value[0]
    if isinstance(value, (str, int, float)):
        return value.strip() if isinstance(value, str) else value
    return None

def extract_metadata(uploaded_file):
    """Extraire les métadonnées générales de l'audit."""
    try:
        wb = load_workbook(uploaded_file)
        ws = wb.active

        metadata = {
            "nom": sanitize_value(get_merged_cell_value(ws, 4, 3)),  # Ligne 4, Colonne C
            "coid": sanitize_value(get_merged_cell_value(ws, 5, 3)),  # Ligne 5, Colonne C
            "referentiel": sanitize_value(get_merged_cell_value(ws, 7, 3)),  # Ligne 7, Colonne C
            "type_audit": sanitize_value(get_merged_cell_value(ws, 8, 3)),  # Ligne 8, Colonne C
            "date_audit": sanitize_value(get_merged_cell_value(ws, 9, 3)),  # Ligne 9, Colonne C
        }

        for key, value in metadata.items():
            if value is None or value == "":
                st.warning(f"Le champ {key} est vide ou invalide.")
                metadata[key] = "Non spécifié"

        return metadata
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def extract_nonconformities(uploaded_file):
    """Extraire les non-conformités depuis la table."""
    try:
        wb = load_workbook(uploaded_file)
        ws = wb.active

        headers = [cell.value for cell in ws[12]]  # Ligne 12
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):  # Lignes à partir de 14
            if any(row):  # Ignorer les lignes vides
                data.append(row)

        return pd.DataFrame(data, columns=headers)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

def insert_into_supabase(metadata, nonconformities):
    """Insérer les données dans Supabase."""
    try:
        # Insérer les métadonnées dans la table "entreprises"
        response = supabase.table("entreprises").insert(metadata).execute()
        if response.status_code != 201:
            st.error(f"Erreur lors de l'insertion des métadonnées : {response.json()}")
            return None
        entreprise_id = response.json()[0]["id"]

        # Ajouter l'ID de l'entreprise à chaque ligne de non-conformité
        nonconformities["entreprise_id"] = entreprise_id

        # Insérer les non-conformités dans la table "nonconformites"
        nonconformities_records = nonconformities.to_dict(orient="records")
        response = supabase.table("nonconformites").insert(nonconformities_records).execute()
        if response.status_code != 201:
            st.error(f"Erreur lors de l'insertion des non-conformités : {response.json()}")
            return None

        st.success("Les données ont été insérées avec succès dans Supabase.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

# Application principale
def main():
    st.title("Extraction et Insertion dans Supabase")

    # Téléversement du fichier Excel
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        # Extraction des métadonnées
        metadata = extract_metadata(uploaded_file)
        if metadata:
            st.write("### Métadonnées de l'Audit")
            st.json(metadata)

        # Extraction des non-conformités
        nonconformities = extract_nonconformities(uploaded_file)
        if nonconformities is not None:
            st.write("### Table des Non-Conformités")
            st.dataframe(nonconformities)

            # Bouton pour insérer dans Supabase
            if st.button("Insérer dans Supabase"):
                insert_into_supabase(metadata, nonconformities)

if __name__ == "__main__":
    main()
