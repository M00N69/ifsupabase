import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit directement avec openpyxl."""
    try:
        wb = load_workbook(file_path)
        ws = wb.active

        # Extraction brute des cellules
        metadata_dict = {
            "Entreprise": ws.cell(row=2, column=2).value,  # Ligne 2, Colonne B
            "COID": ws.cell(row=3, column=2).value,       # Ligne 3, Colonne B
            "Référentiel": ws.cell(row=5, column=2).value,  # Ligne 5, Colonne B
            "Type d'audit": ws.cell(row=6, column=2).value,  # Ligne 6, Colonne B
            "Date de début d'audit": ws.cell(row=7, column=2).value  # Ligne 7, Colonne B
        }

        # Vérifier si des champs sont manquants
        for key, value in metadata_dict.items():
            if value is None:
                st.warning(f"Le champ {key} est vide. Veuillez vérifier le fichier Excel.")

        return metadata_dict

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def extract_nonconformities(file_path):
    """Extraire les non-conformités directement avec openpyxl."""
    try:
        wb = load_workbook(file_path)
        ws = wb.active

        # Début des données des non-conformités à partir de la ligne 13
        start_row = 13
        columns = [
            "requirementno", "requirementtext", "requirementexplanation",
            "correctiondescription", "correctionresponsibility",
            "correctionduedate", "correctionstatus", "correctionevidence",
            "correctiveactiondescription", "correctiveactionresponsibility",
            "correctiveactionduedate", "correctiveactionstatus",
            "releaseresponsibility", "releasedate"
        ]

        # Collecter les données ligne par ligne
        data = []
        for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row, min_col=1, max_col=14):
            row_data = [cell.value for cell in row]
            if any(row_data):  # Ignorer les lignes vides
                data.append(dict(zip(columns, row_data)))

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
            st.error("Les métadonnées contiennent des champs vides. Veuillez vérifier votre fichier.")
            return

        entreprise_response = supabase.table("entreprises").insert(entreprise_data).execute()
        entreprise_id = entreprise_response.data[0]["id"]
        st.success(f"Entreprise ajoutée avec succès. ID: {entreprise_id}")

        # Insertion des non-conformités dans la table 'nonconformites'
        for row in nonconformities:
            # Conversion des dates au format ISO 8601
            if isinstance(row["correctionduedate"], str):
                row["correctionduedate"] = row["correctionduedate"]
            elif row["correctionduedate"]:
                row["correctionduedate"] = row["correctionduedate"].strftime("%Y-%m-%d")

            if isinstance(row["correctiveactionduedate"], str):
                row["correctiveactionduedate"] = row["correctiveactionduedate"]
            elif row["correctiveactionduedate"]:
                row["correctiveactionduedate"] = row["correctiveactionduedate"].strftime("%Y-%m-%d")

            if isinstance(row["releasedate"], str):
                row["releasedate"] = row["releasedate"]
            elif row["releasedate"]:
                row["releasedate"] = row["releasedate"].strftime("%Y-%m-%d")

            # Ajout de l'ID de l'entreprise
            row["entreprise_id"] = entreprise_id

            st.write("Données préparées pour insertion (non-conformités) :", row)
            supabase.table("nonconformites").insert(row).execute()

        st.success("Toutes les non-conformités ont été ajoutées avec succès.")

    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

def main():
    st.title("Chargement des Non-Conformités dans Supabase")

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
        if nonconformities:
            st.write("### Détails des Non-Conformités")
            st.dataframe(nonconformities)

            # Bouton pour envoyer les données dans Supabase
            if st.button("Envoyer les données dans Supabase"):
                insert_data_into_supabase(metadata, nonconformities)

if __name__ == "__main__":
    main()
