from supabase import Client


def check_existing_metadata(client: Client, coid: str) -> bool:
    """Vérifie si une entreprise avec ce COID existe déjà."""
    try:
        response = client.table("entreprises").select("id").eq("coid", coid).execute()
        return len(response.data) > 0
    except Exception as e:
        raise Exception(f"Erreur lors de la vérification des métadonnées : {e}")


def insert_metadata_and_nonconformities(metadata: dict, nonconformities):
    """
    Insère les métadonnées et les non-conformités dans Supabase.
    Retourne un message de succès ou une exception.
    """
    from utils.supabase_client import supabase

    try:
        # Étape 1 : Vérifier si l'entreprise existe
        if check_existing_metadata(supabase, metadata["coid"]):
            return f"L'entreprise avec le COID '{metadata['coid']}' existe déjà. Téléversement ignoré."

        # Étape 2 : Insérer les métadonnées
        response_metadata = supabase.table("entreprises").insert(metadata).execute()
        if not response_metadata.data:
            raise Exception(f"Échec de l'insertion des métadonnées : {response_metadata}")

        entreprise_id = response_metadata.data[0]["id"]

        # Étape 3 : Ajouter l'ID d'entreprise aux non-conformités
        nonconformities["entreprise_id"] = entreprise_id

        # Étape 4 : Insérer les non-conformités
        records = nonconformities.to_dict(orient="records")
        response_nonconformities = supabase.table("nonconformites").insert(records).execute()
        if not response_nonconformities.data:
            raise Exception(
                f"Échec de l'insertion des non-conformités : {response_nonconformities}"
            )

        return "Les métadonnées et non-conformités ont été insérées avec succès."
    except Exception as e:
        raise Exception(f"Erreur lors de l'insertion dans Supabase : {e}")
