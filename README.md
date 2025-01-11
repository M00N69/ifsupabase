# ifsupabase
uplaod de splan d'actions IFS

SUPABASE , VITUNE NCONF

# Audit Non-Conformités Management Application

Cette application Streamlit permet de gérer les non-conformités issues d'audits en téléversant des fichiers Excel, en extrayant les métadonnées et les non-conformités, et en les stockant dans une base de données Supabase. L'application offre également une interface pour visualiser et mettre à jour les non-conformités.

## Fonctionnalités

1. **Téléversement de fichiers Excel** :
   - Téléversez un fichier Excel contenant les données d'audit.
   - Extraction automatique des métadonnées et des non-conformités.
   - Insertion des données dans une base de données Supabase.

2. **Visualisation des Non-Conformités** :
   - Affichez les non-conformités existantes dans une table.
   - Filtrez les non-conformités par COID (identifiant de l'entreprise).

3. **Mise à jour des Non-Conformités** :
   - Mettez à jour les informations des non-conformités directement dans l'interface.
   - Téléversez des fichiers de preuve pour les corrections.

## Structure du Code

### Fichiers Principaux

- **main.py** : Point d'entrée de l'application. Gère la navigation entre les pages et appelle les fonctions appropriées pour chaque page.
- **utils/pages/upload.py** : Contient la logique pour le téléversement des fichiers Excel et l'extraction des données.
- **utils/pages/nonconformities.py** : Contient la logique pour afficher et mettre à jour les non-conformités.
- **utils/supabase_helpers.py** : Contient les fonctions pour interagir avec la base de données Supabase.

### Fonctions Clés

- **extract_metadata(uploaded_file)** : Extrait les métadonnées de l'audit à partir du fichier Excel.
- **extract_nonconformities(uploaded_file)** : Extrait les non-conformités à partir du fichier Excel.
- **insert_into_supabase(metadata, nonconformities)** : Insère les métadonnées et les non-conformités dans Supabase.
- **fetch_nonconformities(coid_filter=None)** : Récupère les non-conformités depuis Supabase, avec un filtre optionnel par COID.
- **update_nonconformity(nonconformity_id, update_data)** : Met à jour une non-conformité dans Supabase.
- **upload_file_to_supabase(file, nonconformity_id)** : Téléverse un fichier de preuve et l'associe à une non-conformité.

## Configuration

1. **Supabase** :
   - Créez un projet sur [Supabase](https://supabase.io/).
   - Configurez les tables `entreprises` et `nonconformites` dans votre base de données.
   - Ajoutez les clés d'API dans les secrets de Streamlit (`st.secrets`).

2. **Streamlit** :
   - Installez les dépendances nécessaires avec `pip install -r requirements.txt`.
   - Exécutez l'application avec `streamlit run main.py`.

## Utilisation

1. **Téléverser un fichier Excel** :
   - Sélectionnez "Téléverser un fichier Excel" dans la barre latérale.
   - Téléversez un fichier Excel conforme au format attendu.
   - Les métadonnées et les non-conformités seront extraites et insérées dans Supabase.

2. **Visualiser les Non-Conformités** :
   - Sélectionnez "Visualiser les Non-Conformités" dans la barre latérale.
   - Utilisez le filtre COID pour afficher les non-conformités spécifiques à une entreprise.

3. **Mettre à jour les Non-Conformités** :
   - Dans la page de visualisation, cliquez sur une non-conformité pour la mettre à jour.
   - Téléversez des fichiers de preuve si nécessaire.

## Dépendances

- `streamlit`
- `pandas`
- `openpyxl`
- `supabase`

## Auteur

[Votre Nom]

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
