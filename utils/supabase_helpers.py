from supabase import Client
import streamlit as st


def check_existing_metadata(client: Client, coid: str):
    """Vérifie si une entreprise avec un COID existe déjà dans Supabase."""
    try:
        response = client.table("entreprises").select("*").eq("coid", coid).execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Erreur lors de la vérification des métadonnées (COID) : {e}")
        return None


def insert_metadata(client: Client, metadata: dict):
    """Insère les métadonnées dans la table 'entreprises'."""
    try:
        # Validation des métadonnées avant insertion
        if not metadata.get("nom") or not metadata.get("coid") or not metadata.get("date_audit"):
            raise ValueError("Les métadonnées sont incomplètes ou mal formatées.")
        
        response = client.table("entreprises").insert(metadata).execute()
        if not response.data:
            raise ValueError(f"Échec de l'insertion des métadonnées : {response}")
        return response.data[0]["id"]  # Retourne l'ID de l'entreprise
    except Exception as e:
        st.error(f"Erreur lors de l'insertion des métadonnées : {e}")
        raise


def insert_nonconformities(client: Client, nonconformities, entreprise_id: str):
    """Insère les non-conformités dans la table 'nonconformites'."""
    try:
        # Validation : Ajouter l'ID de l'entreprise aux non-conformités
        nonconformities["entreprise_id"] = entreprise_id
        records = nonconformities.to_dict(orient="records")

        # Insertion dans Supabase
        response = client.table("nonconformites").insert(records).execute()
        if not response.data:
            raise ValueError(f"Échec de l'insertion des non-conformités : {response}")
        return response.data
    except Exception as e:
        st.error(f"Erreur lors de l'insertion des non-conformités : {e}")
        raise


def update_nonconformity(client: Client, nonconformity_id: str, updates: dict):
    """Met à jour une non-conformité spécifique."""
    try:
        response = client.table("nonconformites").update(updates).eq("id", nonconformity_id).execute()
        if not response.data:
            raise ValueError(f"Échec de la mise à jour : {response}")
        return response.data
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour de la non-conformité : {e}")
        raise


def fetch_coid_list(client: Client):
    """Récupère la liste des COID uniques pour le dropdown."""
    try:
        response = client.table("entreprises").select("coid").execute()
        return [entry["coid"] for entry in response.data if "coid" in entry]
    except Exception as e:
        st.error(f"Erreur lors de la récupération des COID : {e}")
        return []
