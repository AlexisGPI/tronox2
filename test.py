import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, time, timedelta
import locale

from calendar import monthrange
import calendar
import matplotlib.pyplot as plt
import numpy as np

def month_number_to_name(month_number):
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars',
        4: 'Avril', 5: 'Mai', 6: 'Juin',
        7: 'Juillet', 8: 'Août', 9: 'Septembre',
        10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    return month_names.get(month_number, '')



with st.sidebar:

    #st.image("C:/Users/avalentin/Pictures/gpi logo.PNG", width=200)


     # ANNEE ET MOIS *********************************
    annee_en_cours = datetime.now().year
    # Liste des années de 2024 à 2030
    annees = list(range(2024, 2030))
    # Sélectionneur d'année avec l'année en cours sélectionnée par défaut
    selected_year = st.selectbox("Sélectionnez une année", annees, index=annees.index(annee_en_cours))

    date_actuelle = datetime.now()
    # Calculer le mois précédent
    mois_precedent = date_actuelle.replace(day=1) - timedelta(days=1)
    # Liste des noms de mois en français
    mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin","Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    # Index du mois précédent dans la liste des mois
    index_mois_precedent = mois_precedent.month - 1
    # Sélectionneur de mois avec le mois précédent sélectionné par défaut
    selected_month = st.selectbox("Sélectionnez un mois", mois, index=index_mois_precedent)
    #****************************************
   
    # Bouton d'importation de fichier Excel
    uploaded_file = st.file_uploader("Fichier compil préventif", type=['xlsx'])

    uploaded_file2 = st.file_uploader("Fichiert préventif", type=['xlsm'])

    show_raw_data = st.checkbox("Afficher un aperçu des données brutes")




# Créez un dictionnaire pour convertir le mois en français vers son numéro
month_to_number = {
    'Janvier': '1', 'Février': '2', 'Mars': '03', 'Avril': '4', 'Mai': '5', 'Juin': '6',
    'Juillet': '7', 'Août': '8', 'Septembre': '9', 'Octobre': '10', 'Novembre': '11', 'Décembre': '12'
}

# Convertir le nom du mois en numéro
month_number = month_to_number[selected_month]

# Obtenir le dernier jour du mois
_, last_day = monthrange(selected_year, int(month_number))

st.markdown("<p style='text-align: center; line-height: 0.5;font-weight: bold;font-size: 40px'>Rapport d’activité de maintenance</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; line-height: 0.8; font-size: 30px '>Contrat de maintenance E&I</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 20px; line-height: 1.6;'>"
    f"{selected_month} {selected_year} (01/{month_number}/{selected_year} au {last_day}/{month_number}/{selected_year})", unsafe_allow_html=True)



if uploaded_file:
    # Lecture du fichier Excel
    df = pd.read_excel(uploaded_file)

    # Assurez-vous que la première colonne est au format datetime
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])

    # Aperçu des données brutes
    if show_raw_data:
        st.write("Aperçu des données brutes:", df)


    # Ajoute un bouton radio pour la sommation des dépenses
    sum_choice = st.radio('Sommer les dépenses par :', ('Semaine', 'Mois'))

    # Ré-échantillonne les données selon le choix de l'utilisateur
    if sum_choice == 'Semaine':
        df_resampled = df.set_index(df.columns[0]).resample('W').sum().reset_index()
        # Format les semaines comme "S1", "S2", ...
        df_resampled[df.columns[0]] = df_resampled[df.columns[0]].dt.strftime('S%U')
    else:
        df_resampled = df.set_index(df.columns[0]).resample('M').sum().reset_index()
        # Format les mois pour afficher le nom du mois
        df_resampled[df.columns[0]] = df_resampled[df.columns[0]].dt.strftime('%B')

    # Création du graphique avec Altair
    chart = alt.Chart(df_resampled).mark_bar().encode(
        x=alt.X(df.columns[0], title='Période',sort=mois),
        y=alt.Y(df.columns[18], title='Dépense Cumulée'),
        tooltip=[df.columns[0], df.columns[18]]
    ).properties(
        title='Dépenses cumulées par ' + ('semaine' if sum_choice == 'Semaine' else 'mois')
    )

    # Afficher le graphique dans l'application
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("Veuillez télécharger un fichier Excel.")

if uploaded_file2:
    # Lecture du fichier
    df2 = pd.read_excel(uploaded_file2)
    df2['Etat_Renommé'] = df2['Etat'].replace({0: "A faire", 1: "A faire", 2: "Réalisé", 3: "Annulé", 4: "Retard"})
    df2['N° OT'] = df2['N° OT'].astype(str)
    df2['N° PMP'] = df2['N° PMP'].astype(str)

    # Afficher les données brutes si l'option est activée
    if show_raw_data:
        st.write("Aperçu des données brutes:", df2)

    # Choix du mois pour l'analyse
    mois_choisi = st.selectbox("Choisissez un mois:", [0] + list(df2['Mois date de fin'].unique()))

    # Filtrer les données pour le mois choisi (si mois != 0)
    if mois_choisi != 0:
        df_filtre = df2[df2['Mois date de fin'] == mois_choisi]
    else:
        df_filtre = df2

    # Préparer les données pour Altair
    etat_counts = df_filtre['Etat_Renommé'].value_counts().reset_index()
    etat_counts.columns = ['Etat', 'Nombre']
    total = etat_counts['Nombre'].sum()
    etat_counts['Pourcentage'] = etat_counts['Nombre'] / total * 100

     # Créer un graphique à secteurs pour les proportions avec Altair
    base = alt.Chart(etat_counts).encode(
        theta=alt.Theta(field="Nombre", type="quantitative"),
        color=alt.Color(field="Etat", type="nominal"),
        tooltip=[alt.Tooltip(field='Etat', type='nominal'), alt.Tooltip(field='Nombre', type='quantitative')]
    ).mark_arc()

    # Calculer les positions pour les pourcentages
    text_data = etat_counts.copy()
    text_data['midpoint'] = (text_data['Nombre'] / total).cumsum() - (0.5 * text_data['Nombre'] / total)
    text_data['midpoint'] = text_data['midpoint'] * 2 * np.pi
    text = alt.Chart(text_data).mark_text(align='left', baseline='middle', dx=17).encode(
        text=alt.Text('Pourcentage:Q', format='.1f%'),
        x=alt.X('midpoint:Q', scale=alt.Scale(range=[-2*np.pi, 2*np.pi]), axis=None),
        y=alt.Y('midpoint:Q', scale=alt.Scale(range=[-2*np.pi, 2*np.pi]), axis=None)
    )

    chart = (base + text).properties(title=f'Proportion des états pour le mois {mois_choisi}')

    # Afficher le graphique sur Streamlit
    st.altair_chart(chart, use_container_width=True)


    selected_columns = ['Etat', 'N° OT', 'Mois date de fin', 'Etat_Renommé']
    df_selected = df2[selected_columns]


    df_dominant = df_selected.drop_duplicates('N° OT').set_index('N° OT')

    # Réinitialiser l'index
    data = df_dominant.reset_index()
    Nmoischoisi = int(month_number)
    months = range(1,  Nmoischoisi + 1)
    data = data[data['Mois date de fin'].isin(months)]

    
    data['Mois date de fin'] = data['Mois date de fin'].apply(month_number_to_name)


    # Regrouper les données par 'Mois date de fin' et 'Etat_Renommé' et compter les occurrences
    grouped_data = data.groupby(['Mois date de fin', 'Etat_Renommé']).size().reset_index(name='Count')

    # Calculer les totaux pour chaque 'Mois date de fin' pour trouver les proportions
    total_counts = grouped_data.groupby('Mois date de fin')['Count'].transform('sum')

    # Ajouter une colonne pour les proportions
    grouped_data['Proportion'] = grouped_data['Count'] / total_counts

     #Calcul des pourcentages
    grouped_data['Percentage'] = grouped_data['Proportion'] * 100

    # Création du graphique à barres
    bars = alt.Chart(grouped_data).mark_bar().encode(
        x=alt.X('Mois date de fin:N', sort=mois),
        y=alt.Y('Proportion:Q', axis=alt.Axis(format='%')),
        color=alt.Color('Etat_Renommé:N', scale=alt.Scale(
            domain=['A faire', 'Annulé', 'Retard', 'Réalisé'],
            range=['yellow', 'red', 'orange', 'green']
        )),
        tooltip=['Mois date de fin', 'Etat_Renommé', 'Percentage:Q']
    )

    # Ajout de texte sur les barres pour afficher les pourcentages
    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=0  # Ajuster le décalage vertical si nécessaire
    ).encode(
        text=alt.Text('Percentage:Q', format='.1f')
    )

    # Superposition du texte et des barres
    chart = (bars + text).properties(
        title='Proportions de chaque état par mois',
        width=800,
        height=600
    )
     
    # Afficher le graphique
    st.altair_chart(chart)




col1, col2, col3= st.columns([3, 0.25, 2]) 

with col1:

    # Application Streamlit
    st.title('Notes')

    # Champ de saisie de texte pour les notes
    notes = st.text_area("Saisissez vos notes ici:")


with col3:


    # Configurer les paramètres régionaux pour utiliser la langue française
    locale.setlocale(locale.LC_TIME, 'fr_FR')

    # Titre de l'application
    st.markdown("<p style='text-align: center; line-height: 0.8; font-weight: bold; font-size: 30px '>Date de la prochaine réunion</p>", unsafe_allow_html=True)

    # Sélectionneur de date
    selected_date = st.date_input("Choisissez une date")

    # Génère la liste des horaires de 7h00 à 18h00 toutes les 30 minutes
    horaires = [(time(hour=h, minute=m)).strftime('%Hh%M') for h in range(7, 19) for m in (0, 30)]
    # Sélectionneur d'horaire
    selected_time = st.selectbox("Choisissez un horaire", horaires)



