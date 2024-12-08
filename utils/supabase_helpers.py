from supabase import Client

def check_existing_metadata(coid):
    """Vérifie si une entreprise avec le COID donné existe déjà dans Supabase."""
    try:
        response = supabase.table("entreprises").select("id").eq("coid", coid).execute()
        if response.data:
            return True  # L'entreprise existe déjà
        return False
    except Exception as e:
        raise Exception(f"Erreur lors de la vérification du COID : {e}")

def insert_into_supabase(metadata, nonconformities):
    """Insère les métadonnées et les non-conformités dans Supabase."""
    try:
        # Étape 1 : Insérer les métadonnées dans la table 'entreprises'
        response = supabase.table("entreprises").insert(metadata).execute()
        if not response.data:
            raise Exception(f"Erreur lors de l'insertion des métadonnées : {response}")

        # Étape 2 : Récupérer l'ID de l'entreprise insérée
        entreprise_id = response.data[0]["id"]

        # Étape 3 : Ajouter 'entreprise_id' à chaque ligne des non-conformités
        nonconformities["entreprise_id"] = entreprise_id
        records = nonconformities.to_dict(orient="records")

        # Étape 4 : Insérer les non-conformités dans la table 'nonconformites'
        response = supabase.table("nonconformites").insert(records).execute()
        if not response.data:
            raise Exception(f"Erreur lors de l'insertion des non-conformités : {response}")
    except Exception as e:
        raise Exception(f"Erreur lors de l'insertion dans Supabase : {e}")
