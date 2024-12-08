import streamlit as st
from utils.supabase_helpers import fetch_coid_list, fetch_nonconformities, upload_file_to_supabase, update_nonconformity
import pandas as pd

def render_nonconformities_page():
    """Page for viewing and filtering non-conformities."""
    st.title("Gestion des Non-Conformités")

    # Fetch available COIDs for dropdown
    coid_list = fetch_coid_list()
    selected_coid = st.sidebar.selectbox("Filtrer par COID", options=["Tous"] + coid_list)

    # Fetch non-conformities based on the selected COID
    if selected_coid == "Tous":
        nonconformities = fetch_nonconformities()
    else:
        nonconformities = fetch_nonconformities(selected_coid)

    if not nonconformities.empty:
        st.write("### Non-Conformités")
        st.dataframe(nonconformities)

        # Add edit functionality
        for index, row in nonconformities.iterrows():
            with st.expander(f"Éditer la Non-Conformité {row['requirementno']}"):
                with st.form(f"edit_form_{index}"):
                    st.write("### Modifier la Non-Conformité")
                    st.text_area("Exigence", row['requirementtext'], disabled=True)
                    st.text_input("Notation", row['requirementscore'], disabled=True)
                    st.text_area("Explication", row['requirementexplanation'], disabled=True)
                    correction_description = st.text_area(
                        "Correction (par l'entreprise)", value=row['correctiondescription']
                    )
                    correction_responsibility = st.text_input(
                        "Responsabilité (par l'entreprise)", value=row['correctionresponsibility']
                    )
                    correction_due_date = st.date_input(
                        "Date de correction", value=pd.to_datetime(row['correctionduedate'])
                    )
                    correction_status = st.selectbox(
                        "Statut de la correction", options=["En cours", "Soumise", "Validée"], index=0
                    )
                    correction_evidence = st.text_area(
                        "Preuve de correction", value=row['correctionevidence']
                    )
                    corrective_action_description = st.text_area(
                        "Description de l'action corrective", value=row['correctiveactiondescription']
                    )
                    corrective_action_responsibility = st.text_input(
                        "Responsabilité de l'action corrective", value=row['correctiveactionresponsibility']
                    )
                    corrective_action_due_date = st.date_input(
                        "Date de l'action corrective", value=pd.to_datetime(row['correctiveactionduedate'])
                    )
                    corrective_action_status = st.selectbox(
                        "Statut de l'action corrective", options=["En cours", "Soumise", "Validée"], index=0
                    )

                    # File upload for correction evidence
                    uploaded_files = st.file_uploader("Téléverser des fichiers de preuve de correction", accept_multiple_files=True)

                    if st.form_submit_button("Sauvegarder"):
                        try:
                            update_data = {
                                "correctiondescription": correction_description,
                                "correctionresponsibility": correction_responsibility,
                                "correctionduedate": correction_due_date,
                                "correctionstatus": correction_status,
                                "correctionevidence": correction_evidence,
                                "correctiveactiondescription": corrective_action_description,
                                "correctiveactionresponsibility": corrective_action_responsibility,
                                "correctiveactionduedate": corrective_action_due_date,
                                "correctiveactionstatus": corrective_action_status,
                            }
                            update_nonconformity(row['id'], update_data)

                            # Upload files to Supabase
                            if uploaded_files:
                                for file in uploaded_files:
                                    upload_file_to_supabase(file, row['id'])
                        except Exception as e:
                            st.error(f"Erreur lors de la sauvegarde : {e}")
    else:
        st.info("Aucune donnée trouvée pour ce filtre.")
