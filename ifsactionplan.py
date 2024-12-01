import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuration Supabase via Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration de la page
st.set_page_config(page_title="Gestion Non-Conformités", layout="wide")

# Fonction : Récupérer le rôle utilisateur
def get_user_role(email):
    user = supabase.table("utilisateurs").select("*").eq("email", email).execute()
    if user.data:
        return user.data[0]['role'], user.data[0]['entreprise_id']
    return None, None

# Fonction : Lister les fichiers attachés à une non-conformité
def list_files(non_conformite_id):
    files = supabase.table("fichiers").select("*").eq("non_conformite_id", non_conformite_id).execute()
    return files.data

# Fonction : Formulaire d'édition de non-conformité
def edit_nonconformity(nonconformity, role):
    with st.form(key=f"form_edit_{nonconformity['id']}"):
        st.write("### Modifier Non-Conformité")
        st.text_input("Numéro d'exigence", nonconformity["requirementNo"], disabled=True)
        st.text_area("Description de la non-conformité", nonconformity["requirementText"], disabled=True)
        correction = st.text_area("Correction proposée", nonconformity.get("correctionDescription", ""))
        corrective_action = st.text_area("Action corrective", nonconformity.get("correctiveActionDescription", ""))
        
        # Statut pour l'auditeur
        if role == "Auditeur":
            status = st.selectbox(
                "Statut",
                options=["En cours", "Soumise", "Validée"],
                index=["En cours", "Soumise", "Validée"].index(nonconformity.get("correctionStatus", "En cours"))
            )
        else:
            status = nonconformity.get("correctionStatus", "En cours")
            st.write(f"Statut actuel : {status}")

        # Gestion des fichiers attachés
        st.write("### Pièces jointes")
        attached_files = list_files(nonconformity["id"])
        if attached_files:
            for file in attached_files:
                st.markdown(f"[{file['nom']}]({file['url']}) - Téléversé le {file['date_ajout']}")

        # Téléversement de nouveaux fichiers
        uploaded_files = st.file_uploader("Ajouter des fichiers", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

        # Soumission
        submitted = st.form_submit_button("Enregistrer les modifications")
        if submitted:
            # Mise à jour des données
            data = {
                "correctionDescription": correction,
                "correctiveActionDescription": corrective_action,
                "correctionStatus": status
            }
            supabase.table("nonconformites").update(data).eq("id", nonconformity["id"]).execute()

            # Téléversement des fichiers
            for file in uploaded_files:
                file_path = f"files/{nonconformity['id']}/{file.name}"
                supabase.storage.from_('files').upload(file_path, file)
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/files/{file_path}"
                supabase.table("fichiers").insert({
                    "non_conformite_id": nonconformity["id"],
                    "nom": file.name,
                    "url": file_url
                }).execute()

            st.success("Modifications enregistrées avec succès!")

# Fonction principale
def main():
    # Authentification utilisateur
    st.title("Connexion")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        role, entreprise_id = get_user_role(email)
        if role:
            st.session_state["role"] = role
            st.session_state["entreprise_id"] = entreprise_id
            st.session_state["email"] = email
        else:
            st.error("Email ou mot de passe incorrect")

    # Interface utilisateur après connexion
    if "role" in st.session_state:
        role = st.session_state["role"]
        entreprise_id = st.session_state["entreprise_id"]
        st.sidebar.write(f"Utilisateur : {st.session_state['email']}")
        st.sidebar.write(f"Rôle : {role}")

        if role == "Auditeur":
            st.title("Espace Auditeur")
            st.write("### Liste des non-conformités")
            data = supabase.table("nonconformites").select("*").execute()
            for row in data.data:
                st.write(f"**Non-Conformité :** {row['requirementNo']}")
                st.button(f"Modifier {row['requirementNo']}", on_click=edit_nonconformity, args=(row, role))
        elif role == "Audité":
            st.title("Espace Audité")
            st.write("### Mes non-conformités")
            data = supabase.table("nonconformites").select("*").eq("entreprise_id", entreprise_id).execute()
            for row in data.data:
                st.write(f"**Non-Conformité :** {row['requirementNo']}")
                st.button(f"Modifier {row['requirementNo']}", on_click=edit_nonconformity, args=(row, role))

if __name__ == "__main__":
    main()
