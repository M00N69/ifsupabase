def check_existing_metadata(client, coid):
    """Vérifie si une entreprise avec ce COID existe déjà."""
    try:
        response = client.table("entreprises").select("id").eq("coid", coid).execute()
        return bool(response.data)
    except Exception as e:
        raise Exception(f"Erreur lors de la vérification des métadonnées : {e}")


def insert_into_supabase(client, metadata, nonconformities):
    """Insère les métadonnées et les non-conformités dans Supabase."""
    try:
        # Étape 1 : Vérifier si l'entreprise existe
        if check_existing_metadata(client, metadata["coid"]):
            raise ValueError(f"L'entreprise avec le COID '{metadata['coid']}' existe déjà.")

        # Étape 2 : Insérer les métadonnées
        entreprise_response = client.table("entreprises").insert(metadata).execute()
        if not entreprise_response.data:
            raise Exception(f"Erreur lors de l'insertion des métadonnées : {entreprise_response}")

        entreprise_id = entreprise_response.data[0]["id"]

        # Étape 3 : Ajouter l'entreprise ID aux non-conformités
        nonconformities["entreprise_id"] = entreprise_id

        # Étape 4 : Insérer les non-conformités
        records = nonconformities.to_dict(orient="records")
        nc_response = client.table("nonconformites").insert(records).execute()
        if not nc_response.data:
            raise Exception(f"Erreur lors de l'insertion des non-conformités : {nc_response}")

    except Exception as e:
        raise Exception(f"Erreur lors de l'insertion dans Supabase : {e}")
