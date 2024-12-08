import streamlit as st
from utils.supabase_helpers import insert_metadata_and_nonconformities
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

            # Vérification des données extraites
            if metadata and not nonconformities.empty:
                st.success("Données correctement extraites. Prêtes pour l'insertion.")
            else:
                st.error("Erreur : les données extraites sont incomplètes ou incorrectes.")
                return

            # Bouton pour insérer dans Supabase
            if st.button("Insérer dans Supabase"):
                # Appel à la fonction pour insérer dans Supabase
                result_message = insert_metadata_and_nonconformities(
                    metadata, nonconformities
                )
                st.success(result_message)
        except Exception as e:
            st.error(f"Erreur : {e}")
