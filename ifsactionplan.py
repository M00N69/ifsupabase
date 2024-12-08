import pandas as pd
import streamlit as st

# Charger le fichier Excel
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

def extract_nonconformities(file_path):
    """Extraire les non-conformités depuis le tableau principal."""
    try:
        data = pd.read_excel(file_path, sheet_name=0, skiprows=12)  # Sauter les lignes de l'entête
        return data
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

# Interface principale de Streamlit
def main():
    st.title("Extraction des Non-Conformités et Métadonnées")
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

            # Option pour télécharger les non-conformités au format CSV
            csv = nonconformities.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger les Non-Conformités en CSV",
                data=csv,
                file_name='nonconformites.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
