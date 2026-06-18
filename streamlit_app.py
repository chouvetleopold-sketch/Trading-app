import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

st.title("📊 Mon Tableau de Bord PEA Professionnel")
st.write("Sélectionnez une action pour analyser sa santé financière, sa valorisation et ses graphiques de tendance.")

# Liste complète des 120 actions du SBF 120
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
    
    # Les 4 onglets de navigation
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Présentation & Actu", "📈 Analyse Financière", "📊 Graphiques Évolution", "📖 Lexique"])
    
    # ----------------------------------------------------
    # ONGLET 1 : PRÉSENTATION & ACTUALITÉS
    # ----------------------------------------------------
    with tab1:
        st.header(f"🏢 À propos de {info.get('longName', choix)}")
        description = info.get("longBusinessSummary", "Aucune description disponible.")
        st.write(description)
        
        st.markdown("---")
        st.subheader("📰 Dernières Actualités du Titre")
        nouvelles = ticker.news
        actus_valides = [n for n in nouvelles if n.get("title")] if nouvelles else []
        
        if actus_valides:
            for new in actus_valides[:3]:
                st.write(f"**{new.get('title')}**")
                st.write(f"Source : {new.get('publisher', 'Inconnue')} | [Lire l'article]({new.get('link', '#')})")
                st.write("")
        else:
            st.write("Aucune actualité récente disponible.")

    # ----------------------------------------------------
    # ONGLET 2 : ANALYSE FINANCIÈRE AVANCÉE
    # ----------------------------------------------------
    with tab2:
        st.header("🔑 Indicateurs Clés de Performance")
        
        # Extraction des données financières
        prix = info.get("currentPrice", info.get("previousClose", "N/A"))
        per = info.get("trailingPE", "N/A")
        roe = info.get("returnOnEquity", None)
        rendement = info.get("dividendYield", None)
        psr = info.get("priceToSalesTrailing12Months", "N/A")
        marge = info.get("profitMargins", None)
        beta = info.get("beta", "N/A")
        
        # Calcul simplifié de la Capitalisation Boursière
        market_cap = info.get("marketCap", None)
        if market_cap and market_cap >= 1000000000:
            valeur_calculee = round(market_cap / 1000000000, 2)
            market_cap_txt = str(valeur_calculee) + " Md €"
        elif market_cap:
            valeur_calculee = round(market_cap / 1000000, 2)
            market_cap_txt = str(valeur_calculee) + " M €"
        else:
            market_cap_txt = "N/A"
        
        roe_txt = f"{round(roe * 100, 2)}%" if roe else "N/A"
        rendement_txt = f"{round(rendement * 100, 2)}%" if rendement else "0.00%"
        marge_txt = f"{round(marge * 100, 2)}%" if marge else "N/A"
        
        if isinstance(per, (int, float)): per = round(per, 2)
        if isinstance(psr, (int, float)): psr = round(psr, 2)
        if isinstance(beta, (int, float)): beta = round(beta, 2)

        #
