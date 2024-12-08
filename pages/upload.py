import streamlit as st
from utils.supabase_helpers import insert_into_supabase
from utils.data_utils import extract_metadata, extract_nonconformities

def render_upload_page():
    """Page for uploading Excel files."""
    st.title("Téléverser un fichier Excel")
    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])
    if uploaded_file:
        metadata = extract_metadata(uploaded_file)
        nonconformities = extract_nonconformities(uploaded_file)
        if metadata and nonconformities is not None:
            st.write("### Métadonnées")
            st.json(metadata)
            st.write("### Non-Conformités")
            st.dataframe(nonconformities)
            if st.button("Insérer dans Supabase"):
                insert_into_supabase(metadata, nonconformities)
