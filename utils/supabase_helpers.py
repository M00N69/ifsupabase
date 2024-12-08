from supabase import Client


def check_existing_metadata(client: Client, coid):
    """Check if metadata with a specific COID already exists."""
    try:
        response = client.table("entreprises").select("*").eq("coid", coid).execute()
        return response.data
    except Exception as e:
        raise ValueError(f"Erreur lors de la vérification des métadonnées existantes : {e}")


def insert_metadata(client: Client, metadata: dict):
    """Insert metadata into the 'entreprises' table."""
    try:
        response = client.table("entreprises").insert(metadata).execute()
        if not response.data:
            raise ValueError(f"Erreur lors de l'insertion des métadonnées : {response}")
        return response.data[0]["id"]  # Return entreprise_id
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des métadonnées : {e}")


def insert_nonconformities(client: Client, nonconformities, entreprise_id):
    """Insert non-conformities into the 'nonconformites' table."""
    try:
        nonconformities["entreprise_id"] = entreprise_id
        records = nonconformities.to_dict(orient="records")
        response = client.table("nonconformites").insert(records).execute()
        if not response.data:
            raise ValueError(f"Erreur lors de l'insertion des non-conformités : {response}")
        return response.data
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des non-conformités : {e}")


def insert_into_supabase(client: Client, metadata, nonconformities):
    """Insert metadata and non-conformities into Supabase."""
    try:
        existing = check_existing_metadata(client, metadata["coid"])
        if existing:
            return {"status": "warning", "message": "L'entreprise avec ce COID existe déjà."}

        entreprise_id = insert_metadata(client, metadata)
        insert_nonconformities(client, nonconformities, entreprise_id)

        return {"status": "success", "message": "Données insérées avec succès."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
