from supabase import create_client, Client
import pandas as pd
import streamlit as st

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_coid_list():
    """Fetch unique COID values for the dropdown."""
    response = supabase.table("entreprises").select("coid").execute()
    return [entry["coid"] for entry in response.data if "coid" in entry]

def fetch_nonconformities(coid_filter=None):
    """Fetch non-conformities data based on COID filter."""
    query = supabase.table("nonconformites").select("*")
    if coid_filter:
        entreprise_response = supabase.table("entreprises").select("id").eq("coid", coid_filter).execute()
        if entreprise_response.data:
            entreprise_id = entreprise_response.data[0]["id"]
            query = query.eq("entreprise_id", entreprise_id)
    response = query.execute()
    return pd.DataFrame(response.data)

def insert_into_supabase(metadata, nonconformities):
    """Insert metadata and non-conformities into Supabase."""
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
    supabase.table("nonconformites").insert(nonconformities.to_dict(orient="records")).execute()
    st.success("Les données ont été insérées avec succès.")

def update_nonconformity(nonconformity_id, data):
    """Update a non-conformity in Supabase."""
    return supabase.table("nonconformites").update(data).eq("id", nonconformity_id).execute()
