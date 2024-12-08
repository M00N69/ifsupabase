import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client
import pandas as pd

# Configuration Supabase via st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fonction utilitaire pour gérer les valeurs
def sanitize_value(value):
    """Nettoyer et convertir les valeurs pour éviter les erreurs."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return "Non spécifié"
    return str(value)

# Fonction pour extraire les métadonnées
def extract_metadata(uploaded_file):
    """Extraire les métadonnées générales de l'audit."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active

        metadata = {
            "nom": sanitize_value(ws.cell(4, 3).value),  # Ligne 4, Colonne C
            "coid": sanitize_value(ws.cell(5, 3).value),  # Ligne 5, Colonne C
            "referentiel": sanitize_value(ws.cell(7, 3).value),  # Ligne 7, Colonne C
            "type_audit": sanitize_value(ws.cell(8, 3).value),  # Ligne 8, Colonne C
            "date_audit": sanitize_value(ws.cell(9, 3).value),  # Ligne 9, Colonne C
        }

        # Vérification des champs obligatoires
        if not metadata["nom"] or metadata["nom"] == "Non spécifié":
            st.error("Le champ Entreprise est vide. Veuillez vérifier votre fichier Excel.")
        if not metadata["coid"] or metadata["coid"] == "Non spécifié":
            st.error("Le champ COID est vide. Veuillez vérifier votre fichier Excel.")

        return metadata

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

# Fonction pour extraire les non-conformités
def extract_nonconformities(uploaded_file):
    """Extraire les non-conformités depuis le tableau."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active

        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Ligne 12 pour les en-têtes
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):  # Lignes à partir de 14
            if any(row):  # Ignorer les lignes vides
                data.append([sanitize_value(cell) for cell in row])

        return pd.DataFrame(data, columns=headers)

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

# Fonction pour insérer dans Supabase
def insert_into_supabase(metadata, nonconformities):
    """Insérer les données dans Supabase."""
    try:
        # Insérer les métadonnées dans la table "entreprises"
        response = supabase.table("entreprises").insert(metadata).execute()
        if response.status_code != 201:
            st.error(f"Erreur lors de l'insertion des métadonnées : {response.json()}")
            return None
        entreprise_id = response.data[0]["id"]

        # Ajouter l'ID de l'entreprise à chaque ligne de non-conformité
        nonconformities["entreprise_id"] = entreprise_id

        # Préparer les données pour l'insertion
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
