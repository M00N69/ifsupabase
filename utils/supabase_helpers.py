from supabase import create_client, Client
import pandas as pd

def create_supabase_client(url, key):
    """Initialize Supabase client."""
    return create_client(url, key)


def insert_metadata(client: Client, metadata: dict):
    """Insert metadata into the 'entreprises' table."""
    try:
        # Check if the record already exists
        existing = client.table("entreprises").select("*").eq("coid", metadata["coid"]).execute()
        if existing.data:
            return {"status": "warning", "message": "L'entreprise avec ce COID existe déjà."}

        # Insert metadata
        response = client.table("entreprises").insert(metadata).execute()
        if not response.data:
            raise ValueError(f"Erreur lors de l'insertion des métadonnées : {response}")
        return {"status": "success", "data": response.data[0]}
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des métadonnées : {e}")


def insert_nonconformities(client: Client, nonconformities: pd.DataFrame, entreprise_id: str):
    """Insert non-conformities into the 'nonconformites' table."""
    try:
        # Add entreprise_id to each row
        nonconformities["entreprise_id"] = entreprise_id

        # Convert DataFrame to list of records
        records = nonconformities.to_dict(orient="records")

        # Insert into database
        response = client.table("nonconformites").insert(records).execute()
        if not response.data:
            raise ValueError(f"Erreur lors de l'insertion des non-conformités : {response}")
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des non-conformités : {e}")


def insert_into_supabase(client: Client, metadata: dict, nonconformities: pd.DataFrame):
    """Insert both metadata and non-conformities into Supabase."""
    try:
        # Insert metadata
        metadata_response = insert_metadata(client, metadata)
        if metadata_response["status"] != "success":
            return metadata_response

        # Retrieve entreprise_id
        entreprise_id = metadata_response["data"]["id"]

        # Insert non-conformities
        nonconformities_response = insert_nonconformities(client, nonconformities, entreprise_id)
        return nonconformities_response
    except Exception as e:
        raise ValueError(f"Erreur globale lors de l'insertion : {e}")
