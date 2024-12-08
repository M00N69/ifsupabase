import streamlit as st
from openpyxl import load_workbook
import pandas as pd

def extract_metadata(uploaded_file):
    """Extraire les métadonnées générales de l'audit."""
    try:
        wb = load_workbook(uploaded_file)
        ws = wb.active

        # Lecture des cellules spécifiques
        metadata_dict = {
            "Entreprise": ws.cell(row=4, column=3).value,
            "COID": ws.cell(row=5, column=3).value,
            "Numéro client": ws.cell(row=6, column=3).value,
            "Référentiel": ws.cell(row=7, column=3).value,
            "Type d'audit": ws.cell(row=8, column=3).value,
            "Date de début d'audit": ws.cell(row=9, column=3).value,
        }

        # Gérer les valeurs vides
        for key, value in metadata_dict.items():
            if value is None or value == "":
                st.warning(f"Le champ {key} est vide ou invalide. Remplacez-le par 'Non spécifié'.")
                metadata_dict[key] = "Non spécifié"

        return metadata_dict

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None


def extract_nonconformities(uploaded_file):
    """Extraire les non-conformités depuis la table."""
    try:
        wb = load_workbook(uploaded_file)
        ws = wb.active

        # Extraire les en-têtes de la table (ligne 12)
        headers = [cell.value for cell in ws[12]]

        # Extraire les données des lignes suivantes (à partir de la ligne 14)
        data = []
        for row in ws.iter_rows(min_row=14, max_row=ws.max_row, values_only=True):
            if any(row):  # Ignorer les lignes vides
                data.append(row)

        # Convertir en DataFrame pour faciliter l'affichage et la manipulation
        df = pd.DataFrame(data, columns=headers)

        return df

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None


def main():
    st.title("Extraction des Métadonnées et des Non-Conformités")

    # Téléverser un fichier Excel
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

            # Option pour télécharger les non-conformités en CSV
            csv = nonconformities.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger les Non-Conformités en CSV",
                data=csv,
                file_name="nonconformites.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
