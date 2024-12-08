import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Configuration Supabase via st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Utility functions
def sanitize_value(value):
    """Clean and convert values to avoid errors."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        value = value.strip()
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
        return value
    if value in [None, "", " "]:
        return None  # Return None for empty values
    return str(value)

def fetch_coid_list():
    """Fetch unique COID values for the dropdown."""
    try:
        response = supabase.table("entreprises").select("coid").execute()
        coid_list = [entry["coid"] for entry in response.data if "coid" in entry]
        return coid_list
    except Exception as e:
        st.error(f"Erreur lors de la récupération des COID : {e}")
        return []

def fetch_nonconformities(coid_filter=None):
    """Fetch non-conformities data based on COID filter."""
    try:
        query = supabase.table("nonconformites").select("*")
        if coid_filter:
            # Filter non-conformities based on COID
            entreprise_response = supabase.table("entreprises").select("id").eq("coid", coid_filter).execute()
            if entreprise_response.data:
                entreprise_id = entreprise_response.data[0]["id"]
                query = query.eq("entreprise_id", entreprise_id)
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des non-conformités : {e}")
        return pd.DataFrame()

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
    else:
        st.info("Aucune donnée trouvée pour ce filtre.")

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

def extract_metadata(uploaded_file):
    """Extract metadata from the audit."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        metadata = {
            "nom": sanitize_value(ws.cell(4, 3).value),  # Row 4, Col C
            "coid": sanitize_value(ws.cell(5, 3).value),  # Row 5, Col C
            "referentiel": sanitize_value(ws.cell(7, 3).value),  # Row 7, Col C
            "type_audit": sanitize_value(ws.cell(8, 3).value),  # Row 8, Col C
            "date_audit": sanitize_value(ws.cell(9, 3).value),  # Row 9, Col C
        }
        return metadata
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées : {e}")
        return None

def extract_nonconformities(uploaded_file):
    """Extract non-conformities from the table."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active
        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Row 12 headers
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):  # Rows starting at 14
            if any(row):  # Skip empty rows
                data.append([sanitize_value(cell) for cell in row])
        df = pd.DataFrame(data, columns=headers)
        column_mapping = {
            "requirementNo": "requirementno",
            "requirementText": "requirementtext",
            "requirementScore": "requirementscore",
            "requirementExplanation": "requirementexplanation",
            "correctionDescription": "correctiondescription",
            "correctionResponsibility": "correctionresponsibility",
            "correctionDueDate": "correctionduedate",
            "correctionStatus": "correctionstatus",
            "correctionEvidence": "correctionevidence",
            "correctiveActionDescription": "correctiveactiondescription",
            "correctiveActionResponsibility": "correctiveactionresponsibility",
            "correctiveActionDueDate": "correctiveactionduedate",
            "correctiveActionStatus": "correctiveactionstatus",
            "releaseResponsibility": "releaseresponsibility",
            "releaseDate": "releasedate",
        }
        df = df.rename(columns=column_mapping)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

def insert_into_supabase(metadata, nonconformities):
    """Insert metadata and non-conformities into Supabase."""
    try:
        existing = supabase.table("entreprises").select("*").eq("coid", metadata["coid"]).execute()
        if existing.data:
            st.warning("L'entreprise avec ce COID existe déjà. Téléversement ignoré.")
            return
        response = supabase.table("entreprises").insert(metadata).execute()
        if not response.data:
            st.error(f"Erreur lors de l'insertion des métadonnées : {response}")
            return
        entreprise_id = response.data[0]["id"]
        nonconformities["entreprise_id"] = entreprise_id
        nonconformities_records = nonconformities.to_dict(orient="records")
        response = supabase.table("nonconformites").insert(nonconformities_records).execute()
        if not response.data:
            st.error(f"Erreur lors de l'insertion des non-conformités : {response}")
            return
        st.success("Les données ont été insérées avec succès dans Supabase.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

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
