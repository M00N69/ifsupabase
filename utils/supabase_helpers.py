from supabase import create_client, Client

def create_supabase_client(url, key):
    """
    Create a Supabase client.
    Args:
        url (str): Supabase project URL.
        key (str): Supabase API key.
    Returns:
        Client: Supabase client.
    """
    try:
        return create_client(url, key)
    except Exception as e:
        raise ConnectionError(f"Erreur lors de la connexion à Supabase : {e}")

def insert_metadata(client, metadata):
    """
    Insert metadata into the 'entreprises' table.
    Args:
        client (Client): Supabase client.
        metadata (dict): Metadata to insert.
    Returns:
        dict: Response from Supabase.
    """
    try:
        # Check if metadata with the same COID already exists
        existing = client.table("entreprises").select("*").eq("coid", metadata["coid"]).execute()
        if existing.data:
            return {"status": "warning", "message": "L'entreprise avec ce COID existe déjà."}

        response = client.table("entreprises").insert(metadata).execute()
        if response.status_code != 201:
            raise ValueError(f"Erreur lors de l'insertion des métadonnées : {response.json()}")
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des métadonnées : {e}")

def insert_nonconformities(client, nonconformities, entreprise_id):
    """
    Insert non-conformities into the 'nonconformites' table.
    Args:
        client (Client): Supabase client.
        nonconformities (pd.DataFrame): DataFrame of non-conformities.
        entreprise_id (str): ID of the associated enterprise.
    Returns:
        dict: Response from Supabase.
    """
    try:
        nonconformities["entreprise_id"] = entreprise_id
        records = nonconformities.to_dict(orient="records")
        response = client.table("nonconformites").insert(records).execute()
        if response.status_code != 201:
            raise ValueError(f"Erreur lors de l'insertion des non-conformités : {response.json()}")
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise ValueError(f"Erreur lors de l'insertion des non-conformités : {e}")
