import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit."""
    try:
        wb = load_workbook(file_path)
        ws = wb.active

        # Lecture brute des cellules par indices fixes
        metadata_dict = {
            "Entreprise": ws.cell(row=2, column=2).value,  # Ligne 2, Colonne B
            "COID": ws.cell(row=3, column=2).value,       # Ligne 3, Colonne B
            "Référentiel": ws.cell(row=4, column=2).value,  # Ligne 4, Colonne B
            "Type d'audit": ws.cell(row=5, column=2).value,  # Ligne 5, Colonne B
            "Date de début d'audit": ws.cell(row=6, column=2).value  # Ligne 6, Colonne B
        }

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

def main():
    st.title("Chargement des Non-Conformités dans Supabase")
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        metadata = extract_metadata(uploaded_file)
        if metadata:
            st.write("### Métadonnées de l'Audit")
            st.json(metadata)

        nonconformities = extract_nonconformities(uploaded_file)
        if nonconformities:
            st.write("### Détails des Non-Conformités")
            st.write(nonconformities)

if __name__ == "__main__":
    main()
