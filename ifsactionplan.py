import streamlit as st
from openpyxl import load_workbook

def get_merged_cell_value(ws, row, column):
    """
    Obtenir la valeur d'une cellule fusionnée ou d'une cellule normale.
    Si une cellule fusionnée est trouvée, retourne la valeur de la cellule source.
    """
    for merged_range in ws.merged_cells.ranges:
        if (row, column) in merged_range:
            return ws.cell(merged_range.min_row, merged_range.min_col).value
    return ws.cell(row, column).value

def sanitize_value(value):
    """S'assurer que la valeur est une chaîne ou un nombre."""
    if isinstance(value, (str, int, float)):
        return value
    return None

def extract_metadata(file_path):
    """Extraire les métadonnées générales de l'audit avec gestion des cellules fusionnées."""
    try:
        wb = load_workbook(file_path)
        ws = wb.active

        # Lecture brute des cellules
        metadata_dict = {
            "Entreprise": sanitize_value(get_merged_cell_value(ws, 3, 2)),  # Ligne 3, Colonne B
            "COID": sanitize_value(get_merged_cell_value(ws, 4, 2)),       # Ligne 4, Colonne B
            "Référentiel": sanitize_value(get_merged_cell_value(ws, 5, 2)),  # Ligne 5, Colonne B
            "Type d'audit": sanitize_value(get_merged_cell_value(ws, 6, 2)),  # Ligne 6, Colonne B
            "Date de début d'audit": sanitize_value(get_merged_cell_value(ws, 7, 2))  # Ligne 7, Colonne B
        }

        # Vérification des champs vides
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
