import streamlit as st
from utils.pages.upload import render_upload_page
from utils.pages.nonconformities import render_nonconformities_page
from utils.supabase_helpers import update_nonconformity

def main():
    """Main application logic."""
    pages = {
        "Téléverser un fichier Excel": render_upload_page,
        "Visualiser les Non-Conformités": render_nonconformities_page,
    }
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choisissez une page", list(pages.keys()))
    pages[page]()

if __name__ == "__main__":
    main()
