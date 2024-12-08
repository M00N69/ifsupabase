import pandas as pd
import streamlit as st
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit à partir de cellules fixes."""
    try:
        # Charger les données pour les 10 premières lignes du fichier Excel
        metadata = pd.read_excel(file_path, sheet_name=0, header=None, nrows=10, engine='openpyxl')

        # Extraction directe des cellules spécifiques
        metadata_dict = {
            "Entreprise": metadata.iloc[1, 1],  # Ligne 2, Colonne B
            "COID": metadata.iloc[2, 1],       # Ligne 3, Colonne B
            "Référentiel": metadata.iloc[4, 1],  # Ligne 5, Colonne B
            "Type d'audit": metadata.iloc[5, 1],  # Ligne 6, Colonne B
            "Date de début d'audit": metadata.iloc[6, 1]  # Ligne 7, Colonne B
        }

        # Vérification des champs manquants
        for key, value in metadata_dict.items():
            if pd.isna(value):
                st.warning(f"Le champ {key} est manquant ou vide dans le fichier.")

        return metadata_dict

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def extract_nonconformities(file_path):
    """Extraire les non-conformités depuis le tableau principal."""
    try:
        # Charger les non-conformités à partir de la ligne 13
        data = pd.read_excel(file_path, sheet_name=0, skiprows=12, engine='openpyxl')

        # Renommer les colonnes pour correspondre aux champs dans Supabase
        data.rename(columns={
            "requirementNo": "requirementno",
            "requirementText": "requirementtext",
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
            "releaseDate": "releasedate"
        }, inplace=True)

        return data
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

def insert_data_into_supabase(metadata, nonconformities):
    """Insérer les métadonnées et non-conformités dans Supabase."""
    try:
        # Insertion des métadonnées dans la table 'entreprises'
        entreprise_data = {
            "nom": metadata["Entreprise"],
            "coid": metadata["COID"],
            "referentiel": metadata["Référentiel"],
            "type_audit": metadata["Type d'audit"],
            "date_audit": metadata["Date de début d'audit"]
        }
        st.write("Données préparées pour insertion (entreprises) :", entreprise_data)

        if not all(entreprise_data.values()):
            st.error("Les données des métadonnées contiennent des champs vides. Veuillez vérifier votre fichier.")
            return

        entreprise_response = supabase.table("entreprises").insert(entreprise_data).execute()
        entreprise_id = entreprise_response.data[0]["id"]
        st.success(f"Entreprise ajoutée avec succès. ID: {entreprise_id}")

        # Insertion des non-conformités dans la table 'nonconformites'
        for _, row in nonconformities.iterrows():
            # Remplacer les valeurs NaN par None
            row = row.where(pd.notnull(row), None)

            # Convertir les dates au format ISO 8601
            correction_due_date = row["correctionduedate"].strftime("%Y-%m-%d") if row["correctionduedate"] else None
            corrective_action_due_date = row["correctiveactionduedate"].strftime("%Y-%m-%d") if row["correctiveactionduedate"] else None
            release_date = row["releasedate"].strftime("%Y-%m-%d") if row["releasedate"] else None

            nonconformity_data = {
                "entreprise_id": entreprise_id,
                "requirementno": row["requirementno"],
                "requirementtext": row["requirementtext"],
                "requirementexplanation": row["requirementexplanation"],
                "correctiondescription": row["correctiondescription"],
                "correctionresponsibility": row["correctionresponsibility"],
                "correctionduedate": correction_due_date,
                "correctionstatus": row["correctionstatus"],
                "correctionevidence": row["correctionevidence"],
                "correctiveactiondescription": row["correctiveactiondescription"],
                "correctiveactionresponsibility": row["correctiveactionresponsibility"],
                "correctiveactionduedate": corrective_action_due_date,
                "correctiveactionstatus": row["correctiveactionstatus"],
                "releaseresponsibility": row["releaseresponsibility"],
                "releasedate": release_date
            }

            st.write("Données préparées pour insertion (non-conformités) :", nonconformity_data)
            supabase.table("nonconformites").insert(nonconformity_data).execute()

        st.success("Toutes les non-conformités ont été ajoutées avec succès.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

def main():
    st.title("Chargement des Non-Conformités dans Supabase")
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        metadata = extract_metadata(uploaded_file)
        if metadata:
            st.write("### Métadonnées de l'Audit")
            st.json(metadata)

        nonconformities = extract_nonconformities(uploaded_file)
        if nonconformities is not None:
            st.write("### Détails des Non-Conformités")
            st.dataframe(nonconformities)

            if st.button("Envoyer les données dans Supabase"):
                insert_data_into_supabase(metadata, nonconformities)

if __name__ == "__main__":
    main()
