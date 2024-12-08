import streamlit as st
from utils.supabase_helpers import insert_into_supabase, check_existing_metadata
from utils.data_utils import extract_metadata, extract_nonconformities

def render_upload_page():
    """Page for uploading Excel files."""
    st.title("Téléverser un fichier Excel")

    # Téléchargement du fichier Excel
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])
    if uploaded_file:
        # Extraction des métadonnées et non-conformités
        metadata = extract_metadata(uploaded_file)
        nonconformities = extract_nonconformities(uploaded_file)

        if metadata and nonconformities is not None:
            st.success("Fichier traité avec succès.")
            st.write("### Aperçu des Non-Conformités")
            st.dataframe(nonconformities)  # Affichage des non-conformités pour vérification par l'utilisateur

            # Vérifier si l'entreprise existe déjà dans Supabase
            existing_metadata = check_existing_metadata(metadata["coid"])
            if existing_metadata:
                st.warning(
                    f"L'entreprise avec le COID '{metadata['coid']}' existe déjà dans la base de données. "
                    "Aucune donnée ne sera insérée."
                )
            else:
                # Bouton pour insérer les données dans Supabase
                if st.button("Charger les données dans Supabase"):
                    try:
                        insert_into_supabase(metadata, nonconformities)
                        st.success("Les données ont été insérées avec succès dans Supabase.")
                    except Exception as e:
                        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")
        else:
            st.error("Le fichier n'a pas pu être traité. Vérifiez qu'il est bien formaté.")
