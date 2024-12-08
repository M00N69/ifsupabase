import streamlit as st
from openpyxl import load_workbook

def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit."""
    try:
        wb = load_workbook(file_path)
        ws = wb.active

        # Lecture brute des cellules spécifiques
        metadata_dict = {
            "Entreprise": ws.cell(row=3, column=2).value,  # Ligne 3, Colonne B
            "COID": ws.cell(row=4, column=2).value,       # Ligne 4, Colonne B
            "Référentiel": ws.cell(row=6, column=2).value,  # Ligne 6, Colonne B
            "Type d'audit": ws.cell(row=7, column=2).value,  # Ligne 7, Colonne B
            "Date de début d'audit": ws.cell(row=8, column=2).value  # Ligne 8, Colonne B
        }

        # Vérifier les champs manquants ou vides
        for key, value in metadata_dict.items():
            if value is None:
                st.warning(f"Le champ {key} est vide. Veuillez vérifier votre fichier Excel.")

        return metadata_dict

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def main():
    st.title("Extraction des Métadonnées et des Non-Conformités")
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        # Extraction des métadonnées
        metadata = extract_metadata(uploaded_file)
        if metadata:
            st.write("### Métadonnées de l'Audit")
            st.json(metadata)

if __name__ == "__main__":
    main()
