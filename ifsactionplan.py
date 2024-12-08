import streamlit as st
from openpyxl import load_workbook
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Configuration Supabase via st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Allowed values for correctionstatus and other constrained fields
VALID_CORRECTION_STATUS = ["En cours", "Soumise", "Validée"]
VALID_ACTION_STATUS = ["En cours", "Soumise", "Validée"]

def sanitize_value(value):
    """Clean and convert values to avoid errors."""
    if isinstance(value, tuple):
        value = value[0]
    if isinstance(value, str):
        value = value.strip()
        # Try parsing date if applicable
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            pass
        return value
    if value in [None, "", " "]:
        return None  # Return None for empty values
    return str(value)

def validate_enum_value(value, valid_values):
    """Validate enum-like fields and map invalid values to None."""
    if value and value not in valid_values:
        return None  # Replace invalid value with None
    return value

def sanitize_dates(dataframe, date_columns):
    """Ensure date columns are properly formatted or set to None."""
    for date_col in date_columns:
        if date_col in dataframe.columns:
            dataframe[date_col] = dataframe[date_col].apply(
                lambda x: sanitize_value(x) if x else None
            )
    return dataframe

def sanitize_constrained_fields(dataframe):
    """Sanitize fields with constraints like correctionstatus."""
    if "correctionstatus" in dataframe.columns:
        dataframe["correctionstatus"] = dataframe["correctionstatus"].apply(
            lambda x: validate_enum_value(x, VALID_CORRECTION_STATUS) or "En cours"  # Default to 'En cours'
        )
    if "correctiveactionstatus" in dataframe.columns:
        dataframe["correctiveactionstatus"] = dataframe["correctiveactionstatus"].apply(
            lambda x: validate_enum_value(x, VALID_ACTION_STATUS) or "En cours"  # Default to 'En cours'
        )
    return dataframe

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
    """Extract nonconformities from the table."""
    try:
        wb = load_workbook(uploaded_file, data_only=True)
        ws = wb.active

        headers = [sanitize_value(cell.value) for cell in ws[12]]  # Row 12 headers
        data = []
        for row in ws.iter_rows(min_row=14, values_only=True):  # Rows starting at 14
            if any(row):  # Skip empty rows
                data.append([sanitize_value(cell) for cell in row])

        # Rename columns to match 'nonconformites' table fields
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

        # Sanitize date columns
        date_columns = ["correctionduedate", "correctiveactionduedate", "releasedate"]
        df = sanitize_dates(df, date_columns)

        # Sanitize constrained fields
        df = sanitize_constrained_fields(df)

        return df

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des non-conformités : {e}")
        return None

def insert_into_supabase(metadata, nonconformities):
    """Insert metadata and nonconformities into Supabase."""
    try:
        # Check if enterprise already exists
        existing = supabase.table("entreprises").select("id").eq("coid", metadata["coid"]).execute()
        if existing.data:
            st.warning("Cette entreprise avec le même COID existe déjà.")
            return None

        # Insert metadata into the 'entreprises' table
        response = supabase.table("entreprises").insert(metadata).execute()
        
        # Extract the `id` of the inserted enterprise
        entreprise_id = response.data[0]["id"]

        # Add the enterprise ID to each non-conformity row
        nonconformities["entreprise_id"] = entreprise_id

        # Prepare non-conformities data for insertion
        nonconformities_records = nonconformities.to_dict(orient="records")
        response = supabase.table("nonconformites").insert(nonconformities_records).execute()
        
        st.success("Les données ont été insérées avec succès dans Supabase.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")

def main():
    st.title("Chargement des Non-Conformités dans Supabase")

    uploaded_file = st.file_uploader("Téléversez un fichier Excel", type=["xlsx"])

    if uploaded_file:
        metadata = extract_metadata(uploaded_file)

        nonconformities = extract_nonconformities(uploaded_file)
        if nonconformities is not None:
            st.write("### Table des Non-Conformités")
            st.dataframe(nonconformities)

            if st.button("Charger les données"):
                insert_into_supabase(metadata, nonconformities)

if __name__ == "__main__":
    main()
