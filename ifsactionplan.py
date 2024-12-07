import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page Configuration
st.set_page_config(page_title="Gestion Non-Conformités", layout="wide")

# Authentification
def login(email, password):
    """Se connecter via Supabase Auth."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        st.error(f"Erreur lors de la connexion : {e}")
        return None

# Récupération du rôle utilisateur
def get_user_role(auth_user_id):
    """Récupérer le rôle et l'entreprise de l'utilisateur."""
    response = supabase.table("Utilisateurs").select("*").eq("auth_user_id", auth_user_id).execute()
    if response.data:
        return response.data[0]
    return None

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
            send_email_notification(data)
        else:
            st.error("Erreur lors de l'ajout de la non-conformité.")
    except Exception as e:
        st.error(f"Erreur : {e}")

# Envoyer une notification par e-mail
def send_email_notification(data):
    """Envoyer une notification par e-mail."""
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    subject = "Nouvelle Non-Conformité Ajoutée"
    body = f"Une nouvelle non-conformité a été ajoutée :\n\n{data}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        st.success("Notification envoyée par e-mail.")
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'e-mail : {e}")

# Formulaire d'édition des non-conformités
def edit_nonconformity(nonconformity, role):
    """Formulaire pour modifier une non-conformité."""
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

        # Téléversement de fichiers
        uploaded_files = st.file_uploader("Ajouter des fichiers", type=["pdf", "png", "jpg"], accept_multiple_files=True)

        submitted = st.form_submit_button("Enregistrer les modifications")
        if submitted:
            # Mise à jour des données dans la base
            data = {
                "correctionDescription": correction,
                "correctiveActionDescription": corrective_action,
                "correctionStatus": status,
                "date_submission": datetime.utcnow() if status == "Soumise" else None,
            }
            supabase.table("NonConformites").update(data).eq("id", nonconformity["id"]).execute()

            # Téléversement des fichiers
            for file in uploaded_files:
                file_path = f"files/{nonconformity['id']}/{file.name}"
                supabase.storage.from_('files').upload(file_path, file)
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/files/{file_path}"
                supabase.table("Fichiers").insert({
                    "non_conformite_id": nonconformity["id"],
                    "nom": file.name,
                    "url": file_url,
                }).execute()

            st.success("Modifications enregistrées avec succès!")
            send_email_notification(data)

# Interface principale
def main():
    # Authentification
    st.title("Console de connexion")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        result = login(email, password)
        if result:
            user = result.user
            st.session_state["auth_user_id"] = user["id"]
            user_data = get_user_role(user["id"])
            if user_data:
                st.session_state["role"] = user_data["role"]
                st.session_state["entreprise_id"] = user_data["entreprise_id"]
                st.success(f"Bienvenue {user_data['role']}!")
            else:
                st.error("Utilisateur non configuré dans la base de données.")
        else:
            st.error("Email ou mot de passe incorrect.")

    # Interface pour les utilisateurs connectés
    if "auth_user_id" in st.session_state:
        role = st.session_state["role"]
        entreprise_id = st.session_state["entreprise_id"]

        if role == "Auditeur":
            st.title("Espace Auditeur")
            uploaded_file = st.file_uploader("Télécharger un fichier Excel contenant des non-conformités", type=["xlsx"])
            if uploaded_file:
                df = process_excel_file(uploaded_file)
                if df is not None:
                    for _, row in df.iterrows():
                        add_nonconformity({
                            "entreprise_id": entreprise_id,
                            "requirementNo": row["requirementNo"],
                            "requirementText": row["requirementText"],
                            "requirementExplanation": row.get("requirementExplanation", ""),
                        })

        elif role == "Audité":
            st.title("Espace Audité")
            st.write("### Mes non-conformités")
            search_term = st.text_input("Rechercher par numéro d'exigence")
            status_filter = st.selectbox("Filtrer par statut", options=["Tous", "En cours", "Soumise", "Validée"])

            query = supabase.table("NonConformites").select("*").eq("entreprise_id", entreprise_id)
            if search_term:
                query = query.ilike("requirementNo", f"%{search_term}%")
            if status_filter != "Tous":
                query = query.eq("correctionStatus", status_filter)

            data = query.execute()
            for row in data.data:
                st.write(f"**Numéro d'exigence** : {row['requirementNo']}")
                if st.button(f"Modifier {row['requirementNo']}"):
                    edit_nonconformity(row, role)

            # Rapports et Analyses
            st.write("### Rapports et Analyses")
            report_data = supabase.table("NonConformites").select("*").eq("entreprise_id", entreprise_id).execute()
            if report_data.data:
                df_report = pd.DataFrame(report_data.data)
                st.write("Nombre total de non-conformités :", len(df_report))
                st.write("Non-conformités par statut :", df_report["correctionStatus"].value_counts())
                st.write(df_report)

if __name__ == "__main__":
    main()
