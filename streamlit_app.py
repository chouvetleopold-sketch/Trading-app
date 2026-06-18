import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

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

# --- BLOC MODIFIÉ : GRAND BANDEAU GLOBAL EN COULEUR ---
# On crée un conteneur HTML/CSS pour le fond et les textes fixes
st.markdown(
    """
    <div style="background-color: #6B6B2F; padding: 30px; border-radius: 8px; margin-bottom: 20px; color: white; font-family: sans-serif;">
        <h1 style="color: white; margin: 0 0 10px 0; font-size: 2.5rem;">📉 Mon Tableau de Bord PEA Professionnel</h1>
        <p style="margin: 0 0 20px 0; font-size: 1.1rem; opacity: 0.9;">Sélectionnez une action pour analyser sa santé financière, sa valorisation et ses graphiques de tendance.</p>
        <p style="margin: 0 0 5px 0; font-weight: bold; font-size: 1rem;">Choisissez une action à analyser :</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# On place le menu déroulant juste sous le texte d'instruction du bandeau
choix = st.selectbox("", sorted(liste_actions), label_visibility="collapsed")

# Petit espace visuel avant les onglets
st.markdown("<br>", unsafe_allow_html=True)

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
        
        prix = info.get("currentPrice", info.get("previousClose", "N/A"))
        per = info.get("trailingPE", "N/A")
        roe = info.get("returnOnEquity", None)
        rendement = info.get("dividendYield", None)
        psr = info.get("priceToSalesTrailing12Months", "N/A")
        marge = info.get("profitMargins", None)
        beta = info.get("beta", "N/A")
        
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

        col1, col2, col3 = st.columns(3)
        col1.metric("Prix Actuel", f"{prix} €" if prix != "N/A" else "N/A")
        col2.metric("PER (Valorisation)", f"{per}")
        col3.metric("ROE (Rentabilité)", roe_txt)
        
        st.markdown("---")
        
        col4, col5, col6 = st.columns(3)
        col4.metric("Rendement Dividende", rendement_txt)
        col5.metric("Marge Bénéficiaire", marge_txt)
        col6.metric("Price-to-Sales (PSR)", f"{psr}")
        
        st.markdown("---")
        
        col7, col8 = st.columns(2)
        col7.metric("Capitalisation Boursière (Taille)", market_cap_txt)
        col8.metric("Bêta (Volatilité)", f"{beta} (Marché = 1)")

    # ----------------------------------------------------
    # ONGLET 3 : GRAPHIQUES INTERACTIFS
    # ----------------------------------------------------
    with tab3:
        st.header("📈 Historique du Cours & Analyse Technique")
        
        periode = st.radio("Sélectionnez la période historique :", ["1 mois", "1 an", "5 ans"], horizontal=True)
        mapping_periode = {"1 mois": "1mo", "1 an": "1y", "5 ans": "5y"}
        
        historique = ticker.history(period=mapping_periode[periode])
        
        if not historique.empty:
            if periode in ["1 an", "5 ans"] and len(historique) >= 200:
                historique['MA200'] = historique['Close'].rolling(window=200).mean()
            else:
                historique['MA200'] = None
                
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=historique.index, 
                y=historique['Close'], 
                mode='lines', 
                name='Prix de Clôture',
                line=dict(color='#00b4d8', width=2)
            ))
            
            if historique['MA200'].notna().any():
                fig.add_trace(go.Scatter(
                    x=historique.index, 
                    y=historique['MA200'], 
                    mode='lines', 
                    name='Moyenne Mobile 200 jours',
                    line=dict(color='#ff4d6d', width=1.5, dash='dash')
                ))
            
            fig.update_layout(
                title=f"Évolution du cours - {info.get('longName', choix)}",
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                template="plotly_dark",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Impossible de charger les données graphiques pour cette action.")

    # ----------------------------------------------------
    # ONGLET 4 : LEXIQUE DU LANGAGE FINANCIER
    # ----------------------------------------------------
    with tab4:
        st.header("📖 Lexique pour comprendre les indicateurs")
        st.write("Voici l'explication simple de toutes les métriques affichées dans l'onglet Analyse Financière :")
        
        st.subheader("🔹 PER (Price Earnings Ratio)")
        st.write("**Ce que c'est :** Le coefficient de valorisation de l'entreprise.")
        st.write("Il indique combien de fois vous payez le bénéfice annuel de l'entreprise en achetant l'action. Un PER de 15 signifie que l'action s'achète 15 fois son bénéfice. S'il est très élevé (ex: > 30), l'action est jugée chère. S'il est bas, elle peut être sous-évaluée.")
        
        st.subheader("🔹 ROE (Return on Equity)")
        st.write("**Ce que c'est :** La rentabilité des capitaux propres.")
        st.write("Il mesure l'efficacité avec laquelle l'entreprise utilise l'argent de ses actionnaires pour générer du profit. Un ROE supérieur à 12-15% est le signe d'une entreprise très performante financièrement.")
        
        st.subheader("🔹 Rendement du Dividende")
        st.write("**Ce que c'est :** Le pourcentage de gain annuel versé par l'entreprise sous forme de cash.")
        st.write("Si le rendement est de 4%, cela signifie que pour 100€ investis, l'entreprise vous reverse 4€ chaque année. Idéal pour une stratégie de revenus passifs dans un PEA.")
        
        st.subheader("🔹 Marge Bénéficiaire")
        st.write("**Ce que c'est :** Le pourcentage du chiffre d'affaires qui se transforme en bénéfice net.")
        st.write("Une marge de 15% signifie que sur 100€ de ventes, il reste 15€ de pur profit dans les caisses de l'entreprise une fois toutes les factures payées. Plus elle est élevée, plus l'entreprise est solide face à la concurrence.")
        
        st.subheader("🔹 Price-to-Sales (PSR)")
        st.write("**Ce que c'est :** Le ratio Cours / Chiffre d'Affaires.")
        st.write("Il compare la valeur de l'entreprise à ses ventes totales. Un PSR inférieur à 1 ou 2 est souvent considéré comme intéressant. Très utile pour analyser des sociétés en forte croissance qui n'ont pas encore de gros bénéfices nets.")
        
        st.subheader("🔹 Capitalisation Boursière")
        st.write("**Ce que c'est :** La valeur totale de l'entreprise sur le marché.")
        st.write("C'est le prix global qu'il faudrait payer pour acheter 100% de l'entreprise aujourd'hui. Elle s'exprime en Millions (M €) ou Milliards (Md €).")
        
        st.subheader("🔹 Bêta (Volatilité)")
        st.write("**Ce que c'est :** L'indicateur de nervosité de l'action par rapport au marché général.")
        st.write("Le marché de référence a un Bêta de 1. Si l'action a un Bêta de 1.5, elle est plus réactive : si le marché monte de 10%, elle aura tendance à monter de 15%. Si elle a un Bêta de 0.6, elle est très calme.")
