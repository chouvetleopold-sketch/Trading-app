# 1. Installation des outils nécessaires pour l'interface graphique

import streamlit as st
import yfinance as yf
import pandas as pd

# 2. Titre de l'application
st.title("📊 Mon Tableau de Bord PEA Personnel")
st.write("Sélectionnez une action pour voir sa santé financière, son activité et son actu.")

# 3. Barre de recherche ou liste déroulante
liste_actions = ["MC.PA", "OR.PA", "AIR.PA", "TTE.PA", "SAN.PA", "AI.PA"]
choix = st.selectbox("Choisissez une action à analyser :", liste_actions)

if choix:
    ticker = yf.Ticker(choix)
    info = ticker.info
    
    # --- SECTION 1 : SYNTHÈSE DE L'ENTREPRISE ---
    st.header(f"🏢 À propos de {info.get('longName', choix)}")
    # Traduction automatique ou texte brut de la description officielle
    description = info.get("longBusinessSummary", "Aucune description disponible.")
    st.write(description)
    
    st.markdown("---")
    
    # --- SECTION 2 : LES CHIFFRES CLÉS ---
    st.header("📈 Chiffres Clés & Algorithme")
    
    prix = info.get("currentPrice", info.get("previousClose", "N/A"))
    per = info.get("trailingPE", "N/A")
    roe = info.get("returnOnEquity", None)
    roe_txt = f"{round(roe * 100, 2)}%" if roe else "N/A"
    
    # Affichage sous forme de jolies cartes "KPI"
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Actuel", f"{prix} €")
    col2.metric("PER (Valorisation)", f"{per}")
    col3.metric("ROE (Rentabilité)", roe_txt)
    
    st.markdown("---")
    
    # --- SECTION 3 : L'ACTUALITÉ DU TITRE ---
    st.header("📰 Dernières Actualités")
    nouvelles = ticker.news
    
    if nouvelles:
        for new in nouvelles[:3]: # On affiche les 3 dernières actus
            st.subheader(new.get("title"))
            st.write(f"Source : {new.get('publisher')} | Lien : {new.get('link')}")
    else:
        st.write("Aucune actualité récente trouvée pour ce titre.")
