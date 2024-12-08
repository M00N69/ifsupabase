import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Configuration Supabase via st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

        # Ensure date fields are correctly formatted and handle empty values
        for record in nonconformities_records:
            for key in ["correctionduedate", "correctiveactionduedate", "releasedate"]:
                if key in record and record[key]:
                    try:
                        record[key] = datetime.strptime(record[key], "%Y-%m-%d").strftime("%Y-%m-%d")
                    except ValueError:
                        record[key] = None
                elif key in record:
                    record[key] = None

            # Ensure correctionstatus has a valid value
            if "correctionstatus" not in record or not record["correctionstatus"]:
                record["correctionstatus"] = "En cours"  # Set a default value if empty

        response = supabase.table("nonconformites").insert(nonconformities_records).execute()
        if not response.data:
            st.error(f"Erreur lors de l'insertion des non-conformités : {response}")
            return
        st.success("Les données ont été insérées avec succès dans Supabase.")
    except Exception as e:
        st.error(f"Erreur lors de l'insertion dans Supabase : {e}")
