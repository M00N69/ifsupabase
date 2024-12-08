import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Page Configuration
st.set_page_config(page_title="Gestion Non-Conformités", layout="wide")

# Téléversement d'un fichier Excel
def process_excel_file(uploaded_file):
    """Charger et traiter un fichier Excel contenant les non-conformités."""
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu des non-conformités :", df.head())
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

# Ajouter une non-conformité dans la base
def add_nonconformity(data):
    """Ajouter une non-conformité dans la table NonConformites."""
    try:
        response = supabase.table("NonConformites").insert(data).execute()
        if response.status_code == 201:
            st.success("Non-conformité ajoutée avec succès.")
        else:
            st.error("Erreur lors de l'ajout de la non-conformité.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# Téléversement de fichiers associés à une non-conformité
def upload_files(non_conformity_id, uploaded_files):
    """Téléverser des fichiers dans le bucket Supabase Storage."""
    for file in uploaded_files:
        file_path = f"files/{non_conformity_id}/{file.name}"
        supabase.storage.from_('files').upload(file_path, file)
        file_url = f"{SUPABASE_URL}/storage/v1/object/public/files/{file_path}"
        supabase.table("Fichiers").insert({
            "non_conformite_id": non_conformity_id,
            "nom": file.name,
            "url": file_url,
            "date_ajout": datetime.utcnow()
        }).execute()

# Formulaire d'édition des non-conformités
def edit_nonconformity(nonconformity):
    """Formulaire pour modifier une non-conformité."""
    with st.form(key=f"form_edit_{nonconformity['id']}"):
        st.write("### Modifier Non-Conformité")
        st.text_input("Numéro d'exigence", nonconformity["requirementNo"], disabled=True)
        st.text_area("Description de la non-conformité", nonconformity["requirementText"], disabled=True)
        correction = st.text_area("Correction proposée", nonconformity.get("correctionDescription", ""))
        corrective_action = st.text_area("Action corrective", nonconformity.get("correctiveActionDescription", ""))
        status = st.selectbox(
            "Statut",
            options=["En cours", "Soumise", "Validée"],
            index=["En cours", "Soumise", "Validée"].index(nonconformity.get("correctionStatus", "En cours"))
        )
        uploaded_files = st.file_uploader("Ajouter des fichiers", type=["pdf", "png", "jpg"], accept_multiple_files=True)

        submitted = st.form_submit_button("Enregistrer les modifications")
        if submitted:
            # Mise à jour des données
            data = {
                "correctionDescription": correction,
                "correctiveActionDescription": corrective_action,
                "correctionStatus": status,
                "date_submission": datetime.utcnow() if status == "Soumise" else None
            }
            supabase.table("NonConformites").update(data).eq("id", nonconformity["id"]).execute()
            if uploaded_files:
                upload_files(nonconformity["id"], uploaded_files)
            st.success("Modifications enregistrées avec succès!")

# Interface principale
def main():
    st.title("Gestion des Non-Conformités")
    uploaded_file = st.file_uploader("Téléchargez un fichier Excel", type=["xlsx"])
    if uploaded_file:
        df = process_excel_file(uploaded_file)
        if df is not None:
            for _, row in df.iterrows():
                add_nonconformity({
                    "entreprise_id": "entreprise-id-uuid",
                    "requirementNo": row["requirementNo"],
                    "requirementText": row["requirementText"],
                    "requirementExplanation": row.get("requirementExplanation", ""),
                })

    st.write("### Liste des Non-Conformités")
    nonconformities = supabase.table("NonConformites").select("*").execute()
    for nc in nonconformities.data:
        st.write(f"**Numéro d'exigence** : {nc['requirementNo']}")
        st.button(f"Modifier {nc['requirementNo']}", on_click=edit_nonconformity, args=(nc,))

if __name__ == "__main__":
    main()
