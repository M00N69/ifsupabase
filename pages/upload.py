import streamlit as st
from utils.supabase_helpers import insert_into_supabase
from utils.data_utils import extract_metadata, extract_nonconformities


def render_upload_page():
    """Page pour téléverser un fichier Excel et insérer les données dans Supabase."""
    st.title("Téléverser un fichier Excel")

    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        try:
            # Extraction des métadonnées et non-conformités
            metadata = extract_metadata(uploaded_file)
            nonconformities = extract_nonconformities(uploaded_file)

            # Affichage des résultats
            st.write("### Métadonnées")
            st.json(metadata)
            st.write("### Non-Conformités")
            st.dataframe(nonconformities)

            # Bouton pour insérer dans Supabase
            if st.button("Insérer dans Supabase"):
                insert_into_supabase(st.secrets["supabase_client"], metadata, nonconformities)
                st.success("Les données ont été insérées avec succès.")
        except Exception as e:
            st.error(f"Erreur : {e}")
