import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Titre de l'application
st.title("📊 Mon Tableau de Bord PEA Personnel")
st.write("Sélectionnez une action pour voir sa santé financière, son activité et son actu.")

# --- LISTE COMPLÈTE DES 120 ACTIONS DU SBF 120 ---
liste_actions = [
    "AC.PA", "ACA.PA", "AI.PA", "AIR.PA", "ALD.PA", "ALO.PA", "ALT.PA", "AMUN.PA", "ATE.PA",
    "ATO.PA", "BALO.PA", "BAM.PA", "BBO.PA", "BCP.PA", "BEN.PA", "BIM.PA", "BNP.PA", "BOLL.PA", "BOUY.PA",
    "CAFP.PA", "CAP.PA", "CARA.PA", "CARR.PA", "CDI.PA", "CEG.PA", "CHG.PA", "CIE.PA", "COFA.PA", "COV.PA",
    "CS.PA", "DBV.PA", "DEC.PA", "DERI.PA", "DFV.PA", "DG.PA", "DIM.PA", "DSY.PA", "EDEN.PA", "EDF.PA",
    "EN.PA", "ENGI.PA", "ERA.PA", "ERI.PA", "ETL.PA", "EURA.PA", "EVO.PA", "FDJ.PA", "FR.PA", "FTI.PA",
    "GFC.PA", "GLE.PA", "GTT.PA", "HO.PA", "ICAD.PA", "IDL.PA", "ILD.PA", "IMPL.PA", "INE.PA", "ING.PA",
    "IPS.PA", "IPH.PA", "ITP.PA", "JCQ.PA", "KAF.PA", "KER.PA", "KEY.PA", "KOF.PA", "LI.PA", "LHN.PA",
    "LNA.PA", "LR.PA", "MC.PA", "MERY.PA", "MF.PA", "MMB.PA", "MMT.PA", "NANO.PA", "NEX.PA", "NK.PA",
    "NRO.PA", "NWY.PA", "OR.PA", "ORA.PA", "ORP.PA", "PEUG.PA", "POM.PA", "PUB.PA", "RCO.PA", "RE.PA",
    "RHA.PA", "RI.PA", "RMS.PA", "RNO.PA", "RUN.PA", "SAF.PA", "SAN.PA", "SGO.PA", "SHL.PA", "SK.PA",
    "SBT.PA", "SOI.PA", "SOM.PA", "SOP.PA", "SPIE.PA", "SQI.PA", "SU.PA", "SW.PA", "TEP.PA", "TFI.PA",
    "TI.PA", "TRI.PA", "TTE.PA", "UBI.PA", "URW.PA", "VALL.PA", "VEO.PA", "VGO.PA", "VIE.PA", "VIV.PA",
    "VLA.PA", "VPK.PA", "VRAP.PA", "WLN.PA", "XIL.PA"
]

choix = st.selectbox("Choisissez une action à analyser :", sorted(liste_actions))

if choix:
    ticker = yf.Ticker(choix)
    info = ticker.info
    
    # --- SECTION 1 : SYNTHÈSE DE L'ENTREPRISE ---
    st.header(f"🏢 À propos de {info.get('longName', choix)}")
    description = info.get("longBusinessSummary", "Aucune description disponible.")
    st.write(description)
    
    st.markdown("---")
    
    # --- SECTION 2 : LES CHIFFRES CLÉS ---
    st.header("📈 Chiffres Clés & Algorithme")
    
    prix = info.get("currentPrice", info.get("previousClose", "N/A"))
    per = info.get("trailingPE", "N/A")
    roe = info.get("returnOnEquity", None)
    roe_txt = f"{round(roe * 100, 2)}%" if roe else "N/A"
    
    # Arrondir proprement le PER s'il existe
    if isinstance(per, (int, float)):
        per = round(per, 2)
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Actuel", f"{prix} €" if prix != "N/A" else "N/A")
    col2.metric("PER (Valorisation)", f"{per}")
    col3.metric("ROE (Rentabilité)", roe_txt)
    
    st.markdown("---")
    
    # --- SECTION 3 : L'ACTUALITÉ DU TITRE ---
    st.header("📰 Dernières Actualités")
    nouvelles = ticker.news
    
    # On filtre pour afficher uniquement les actus qui ont un vrai titre
    actus_valides = [n for n in nouvelles if n.get("title")] if nouvelles else []
    
    if actus_valides:
        for new in actus_valides[:3]: # On affiche les 3 dernières vraies actus
            st.subheader(new.get("title"))
            source = new.get("publisher", "Inconnue")
            lien = new.get("link", "#")
            st.write(f"Source : {source} | [Lire l'article]({lien})")
    else:
        st.write("Aucune actualité récente disponible sur Yahoo Finance pour ce titre.")
