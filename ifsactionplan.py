import pandas as pd
import streamlit as st
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fonction pour extraire les métadonnées
def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit."""
    try:
        metadata = pd.read_excel(file_path, sheet_name=0, header=None, nrows=10)
        metadata_dict = {
            "Entreprise": metadata.iloc[1, 1],
            "COID": metadata.iloc[2, 1],
            "Référentiel": metadata.iloc[3, 1],
            "Type d'audit": metadata.iloc[4, 1],
            "Date de début d'audit": metadata.iloc[5, 1]
        }
        return metadata_dict
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

# Fonction pour extraire les non-conformités
def extract_nonconformities(file_path):
    """Extraire les non-conformités depuis le tableau principal."""
    try:
        data = pd.read_excel(file_path, sheet_name=0, skiprows=12)  # Sauter les lignes de l'entête
        return data
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

# Fonction pour insérer les données dans Supabase
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
        st.write("Insertion des métadonnées : ", entreprise_data)
        entreprise_response = supabase.table("entreprises").insert(entreprise_data).execute()
        entreprise_id = entreprise_response.data[0]["id"]
        st.success(f"Entreprise ajoutée avec succès. ID: {entreprise_id}")

        # Insertion des non-conformités dans la table 'nonconformites'
        for _, row in nonconformities.iterrows():
            # Remplacer les valeurs NaN par None
            row = row.where(pd.notnull(row), None)

            # Convertir les dates au format ISO 8601
            correction_due_date = row["correctionDueDate"].strftime("%Y-%m-%d") if row["correctionDueDate"] else None
            corrective_action_due_date = row["correctiveActionDueDate"].strftime("%Y-%m-%d") if row["correctiveActionDueDate"] else None
            release_date = row["releaseDate"].strftime("%Y-%m-%d") if row["releaseDate"] else None

            nonconformity_data = {
                "entreprise_id": entreprise_id,
                "requirementno": row["requirementNo"],
                "requirementtext": row["requirementText"],
                "requirementexplanation": row["requirementExplanation"],
                "correctiondescription": row["correctionDescription"],
                "correctionresponsibility": row["correctionResponsibility"],
                "correctionduedate": correction_due_date,
                "correctionstatus": row["correctionStatus"],
                "correctionevidence": row["correctionEvidence"],
                "correctiveactiondescription": row["correctiveActionDescription"],
                "correctiveactionresponsibility": row["correctiveActionResponsibility"],
                "correctiveactionduedate": corrective_action_due_date,
                "correctiveactionstatus": row["correctiveActionStatus"],
                "releaseResponsibility": row["releaseResponsibility"],
                "releaseDate": release_date
            }

            st.write("Données préparées pour insertion :", nonconformity_data)
            supabase.table("nonconformites").insert(nonconformity_data).execute()

        st.success("Toutes les non-conformités ont été ajoutées avec succès.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

# Interface principale de Streamlit
def main():
    st.title("Chargement des Non-Conformités dans Supabase")
    st.write("Téléchargez un fichier Excel contenant les non-conformités.")

    # Téléversement du fichier
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
            st.write("### Détails des Non-Conformités")
            st.dataframe(nonconformities)

            # Insertion des données dans Supabase
            if st.button("Envoyer les données dans Supabase"):
                insert_data_into_supabase(metadata, nonconformities)

if __name__ == "__main__":
    main()

