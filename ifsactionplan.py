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
    """Ajouter une non-conformité dans la table non_conformities."""
    try:
        response = supabase.table("non_conformities").insert(data).execute()
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
        st.text_input("Numéro d'exigence", nonconformity["object"], disabled=True)
        st.text_area("Description de la non-conformité", nonconformity["description"], disabled=True)
        correction = st.text_area("Correction proposée", nonconformity.get("correctionDescription", ""))
        corrective_action = st.text_area("Action corrective", nonconformity.get("correctiveActionDescription", ""))

        # Statut pour l'auditeur
        if role == "Auditeur":
            status = st.selectbox(
                "Statut",
                options=["En cours", "Soumise", "Validée"],
                index=["En cours", "Soumise", "Validée"].index(nonconformity.get("status", "En cours"))
            )
        else:
            status = nonconformity.get("status", "En cours")
            st.write(f"Statut actuel : {status}")

        # Téléversement de fichiers
        uploaded_files = st.file_uploader("Ajouter des fichiers", type=["pdf", "png", "jpg"], accept_multiple_files=True)

        submitted = st.form_submit_button("Enregistrer les modifications")
        if submitted:
            # Mise à jour des données dans la base
            data = {
                "correctionDescription": correction,
                "correctiveActionDescription": corrective_action,
                "status": status,
                "updated_at": datetime.utcnow() if status == "Soumise" else None,
            }
            supabase.table("non_conformities").update(data).eq("id", nonconformity["id"]).execute()

            # Téléversement des fichiers
            for file in uploaded_files:
                file_path = f"files/{nonconformity['id']}/{file.name}"
                supabase.storage.from_('non-conformity-images').upload(file_path, file)
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/non-conformity-images/{file_path}"
                supabase.table("non_conformities").update({"images": supabase.functions.array_append("images", file_url)}).eq("id", nonconformity["id"]).execute()

            st.success("Modifications enregistrées avec succès!")
            send_email_notification(data)

# Interface principale
def main():
    # Interface pour les utilisateurs connectés
    st.session_state["role"] = "Auditeur"  # Définir le rôle par défaut
    st.session_state["user_id"] = "example_user_id"  # Définir un user_id par défaut

    if st.session_state["role"] == "Auditeur":
        st.title("Espace Auditeur")
        uploaded_file = st.file_uploader("Télécharger un fichier Excel contenant des non-conformités", type=["xlsx"])
        if uploaded_file:
            df = process_excel_file(uploaded_file)
            if df is not None:
                for _, row in df.iterrows():
                    add_nonconformity({
                        "user_id": st.session_state["user_id"],
                        "object": row["object"],
                        "type": row["type"],
                        "description": row["description"],
                        "status": row.get("status", "En cours"),
                        "images": []
                    })

    elif st.session_state["role"] == "Audité":
        st.title("Espace Audité")
        st.write("### Mes non-conformités")
        search_term = st.text_input("Rechercher par numéro d'exigence")
        status_filter = st.selectbox("Filtrer par statut", options=["Tous", "En cours", "Soumise", "Validée"])

        query = supabase.table("non_conformities").select("*").eq("user_id", st.session_state["user_id"])
        if search_term:
            query = query.ilike("object", f"%{search_term}%")
        if status_filter != "Tous":
            query = query.eq("status", status_filter)

        data = query.execute()
        for row in data.data:
            st.write(f"**Numéro d'exigence** : {row['object']}")
            if st.button(f"Modifier {row['object']}"):
                edit_nonconformity(row, st.session_state["role"])

        # Rapports et Analyses
        st.write("### Rapports et Analyses")
        report_data = supabase.table("non_conformities").select("*").eq("user_id", st.session_state["user_id"]).execute()
        if report_data.data:
            df_report = pd.DataFrame(report_data.data)
            st.write("Nombre total de non-conformités :", len(df_report))
            st.write("Non-conformités par statut :", df_report["status"].value_counts())
            st.write(df_report)

if __name__ == "__main__":
    main()
