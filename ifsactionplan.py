import streamlit as st
from openpyxl import load_workbook

def get_merged_cell_value(ws, row, column):
    """Obtenir la valeur d'une cellule fusionnée ou non."""
    for merged_range in ws.merged_cells.ranges:
        if (row, column) in merged_range:
            return ws.cell(merged_range.min_row, merged_range.min_col).value
    return ws.cell(row, column).value

def sanitize_value(value):
    """Nettoyer et s'assurer que la valeur est utilisable."""
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

        metadata_dict = {
            "Entreprise": sanitize_value(get_merged_cell_value(ws, 3, 2)),  # Ligne 3, Colonne B
            "COID": sanitize_value(get_merged_cell_value(ws, 4, 2)),       # Ligne 4, Colonne B
            "Référentiel": sanitize_value(get_merged_cell_value(ws, 5, 2)),  # Ligne 5, Colonne B
            "Type d'audit": sanitize_value(get_merged_cell_value(ws, 6, 2)),  # Ligne 6, Colonne B
            "Date de début d'audit": sanitize_value(get_merged_cell_value(ws, 7, 2))  # Ligne 7, Colonne B
        }

        for key, value in metadata_dict.items():
            if value is None:
                st.warning(f"Le champ {key} est vide ou invalide. Veuillez vérifier votre fichier Excel.")

        return metadata_dict

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def inspect_excel(uploaded_file):
    """Inspecter le contenu brut d'un fichier Excel téléversé via Streamlit."""
    try:
        wb = load_workbook(uploaded_file)
        ws = wb.active
        for row_index, row in enumerate(ws.iter_rows(values_only=True), start=1):
            st.write(f"Ligne {row_index}: {row}")  # Affiche chaque ligne dans Streamlit
    except Exception as e:
        st.error(f"Erreur lors de l'inspection du fichier : {e}")

def main():
    st.title("Extraction des Métadonnées et des Non-Conformités")
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        # Inspection brute pour débogage
        st.write("### Inspection brute du fichier")
        inspect_excel(uploaded_file)

        # Extraction des métadonnées
        metadata = extract_metadata(uploaded_file)
        if metadata:
            st.write("### Métadonnées de l'Audit")
            st.json(metadata)

if __name__ == "__main__":
    main()
