import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

# --- FONCTION : CALCUL DU RSI ---
def calculer_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=False).mean()
    ma_down = down.ewm(com=periods - 1, adjust=False).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi.iloc[-1] if not rsi.empty else 50

# --- FONCTION POUR LE MOMENTUM ET LA VALORISATION (MIS À JOUR) ---
@st.cache_data(ttl=3600)
def obtenir_top_momentum():
    actions_test = {
        "LVMH": "MC.PA", "TotalEnergies": "TTE.PA", "Air Liquide": "AI.PA", 
        "Schneider Electric": "SU.PA", "Sanofi": "SAN.PA", "Airbus": "AIR.DE",
        "ASML": "ASML.AS", "Ferrari": "RACE.MI", "BNP Paribas": "BNP.PA",
        "Saint-Gobain": "SGO.PA", "Hermès": "RMS.PA", "L'Oréal": "OR.PA"
    }
    
    liste_data = []
    for nom, ticker_code in actions_test.items():
        try:
            t = yf.Ticker(ticker_code)
            info = t.info
            hist = t.history(period="1y")
            
            if len(hist) > 200:
                prix_actuel = hist['Close'].iloc[-1]
                prix_an_dernier = hist['Close'].iloc[0]
                perf_1an = ((prix_actuel - prix_an_dernier) / prix_an_dernier) * 100
                
                ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
                au_dessus_ma200 = "Oui 📈" if prix_actuel > ma200 else "Non 📉"
                
                rsi_actuel = calculer_rsi(hist)
                
                # --- CALCUL DE L'ÉVALUATION FINANCIÈRE ---
                per_actuel = info.get("trailingPE", None)
                per_moyen_5ans = info.get("fiveYearAvgTrailingPE", None)
                
                if per_actuel and per_moyen_5ans:
                    # Règle de comparaison PER actuel vs Moyenne 5 ans
                    ratio_val = per_actuel / per_moyen_5ans
                    if ratio_val < 0.85:
                        evaluation = "🟢 Sous-évalué (Décote)"
                    elif ratio_val > 1.15:
                        evaluation = "🔴 Surévalué (Cher)"
                    else:
                        evaluation = "🟡 Prix Juste"
                elif per_actuel:
                    # Secours si la moyenne 5 ans n'est pas dispo
                    if per_actuel < 13: evaluation = "🟢 Sous-évalué (PER bas)"
                    elif per_actuel > 25: evaluation = "🔴 Surévalué (PER haut)"
                    else: evaluation = "🟡 Prix Juste"
                else:
                    evaluation = "📊 N/A (Pas de PER)"
                
                # Diagnostic d'élan technique
                if perf_1an > 10 and prix_actuel > ma200 and 50 <= rsi_actuel <= 75:
                    elan = "🔥 Fort & Sain"
                elif perf_1an > 20 and rsi_actuel > 75:
                    elan = "⚠️ Surchauffe"
                elif perf_1an < 0:
                    elan = "❄️ Baissier"
                else:
                    elan = "⚖️ Neutre"
                
                liste_data.append({
                    "Entreprise": nom,
                    "Code": ticker_code,
                    "Prix Actuel (€)": round(prix_actuel, 2),
                    "Perf. 1 An": f"{round(perf_1an, 2)}%",
                    "Tendance (MA200)": au_dessus_ma200,
                    "RSI (Force 14j)": round(rsi_actuel, 1),
                    "Évaluation Financière": evaluation,
                    "Diagnostic Élan": elan
                })
        except:
            continue
            
    df = pd.DataFrame(liste_data)
    if not df.empty:
        return df.sort_values(by="RSI (Force 14j)", ascending=False)
    return df

# --- BLOC : GRAND BANDEAU GLOBAL EN COULEUR ---
st.markdown(
    """
    <div style="background-color: #6B6B2F; padding: 30px; border-radius: 8px; margin-bottom: 20px; color: white; font-family: sans-serif;">
        <h1 style="color: white; margin: 0 0 10px 0; font-size: 2.5rem;">📉 Mon Grand Moteur de Recherche Boursier</h1>
        <p style="margin: 0 0 20px 0; font-size: 1.1rem; opacity: 0.9;">Analysez une action par son nom ou découvrez la santé financière et l'élan des marchés.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

onglet_principal_1, onglet_principal_2 = st.tabs(["🔍 Rechercher une entreprise", "🚀 Découverte & Momentum Européen"])

# ====================================================================
# ONGLET PRINCIPAL 1 : MOTEUR DE RECHERCHE PAR NOM
# ====================================================================
with onglet_principal_1:
    st.write("### Entrez le nom de l'entreprise à analyser :")
    recherche_utilisateur = st.text_input("", value="LVMH", label_visibility="collapsed").strip()
    st.markdown("<br>", unsafe_allow_html=True)

    if recherche_utilisateur:
        try:
            recherche = yf.Search(recherche_utilisateur, max_results=5)
            resultats = recherche.quotes
            
            if not resultats:
                st.error(f"❌ Aucune entreprise trouvée pour le nom '{recherche_utilisateur}'.")
            else:
                choix = resultats[0]['symbol']
                ticker = yf.Ticker(choix)
                info = ticker.info
                
                if not info or not any(k in info for k in ['regularMarketPrice', 'currentPrice', 'previousClose', 'longName']):
                    st.error(f"❌ Impossible de charger les données pour '{recherche_utilisateur}' (Code : {choix}).")
                else:
                    nom_action = info.get('longName', recherche_utilisateur)
                    st.info(f"🔍 Résultat trouvé : **{nom_action}** (Code boursier : `{choix}`)")
                    
                    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Présentation & Actu", "📈 Analyse Financière", "📊 Graphiques Évolution", "📖 Lexique"])
                    
                    with tab1:
                        st.header(f"🏢 À propos de {nom_action}")
                        st.write(info.get("longBusinessSummary", "Aucune description disponible."))
                        st.markdown("---")
                        st.subheader("📰 Dernières Actualités")
                        nouvelles = ticker.news
                        if nouvelles:
                            for new in nouvelles[:3]:
                                if new.get("title"):
                                    st.write(f"**{new.get('title')}**")
                                    st.write(f"Source : {new.get('publisher', 'Inconnue')} | [Lire l'article]({new.get('link', '#')})")
                        else:
                            st.write("Aucune actualité disponible.")

                    with tab2:
                        st.header(f"🔑 Indicateurs Clés — {nom_action}")
                        prix = info.get("currentPrice", info.get("previousClose", "N/A"))
                        per = info.get("trailingPE", "N/A")
                        roe = info.get("returnOnEquity", None)
                        rendement = info.get("dividendYield", None)
                        psr = info.get("priceToSalesTrailing12Months", "N/A")
                        marge = info.get("profitMargins", None)
                        beta = info.get("beta", "N/A")
                        
                        market_cap = info.get("marketCap", None)
                        market_cap_txt = f"{round(market_cap / 1000000000, 2)} Md €" if market_cap and market_cap >= 1000000000 else "N/A"
                        roe_txt = f"{round(roe * 100, 2)}%" if roe else "N/A"
                        rendement_txt = f"{round(rendement * 100, 2)}%" if rendement else "0.00%"
                        marge_txt = f"{round(marge * 100, 2)}%" if marge else "N/A"
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Prix Actuel", f"{prix} €" if prix != "N/A" else "N/A")
                        col2.metric("PER (Valorisation)", f"{round(per, 2)}" if isinstance(per, (int,float)) else per)
                        col3.metric("ROE (Rentabilité)", roe_txt)
                        
                        st.markdown("---")
                        col4, col5, col6 = st.columns(3)
                        col4.metric("Rendement Dividende", rendement_txt)
                        col5.metric("Marge Bénéficiaire", marge_txt)
                        col6.metric("Price-to-Sales (PSR)", f"{round(psr,2)}" if isinstance(psr, (int,float)) else psr)
                        
                        st.markdown("---")
                        col7, col8 = st.columns(2)
                        col7.metric("Capitalisation Boursière", market_cap_txt)
                        col8.metric("Bêta (Volatilité)", f"{round(beta,2)}" if isinstance(beta, (int,float)) else beta)

                    with tab3:
                        st.header("📈 Historique du Cours")
                        periode = st.radio("Période :", ["1 mois", "1 an", "5 ans"], horizontal=True)
                        mapping = {"1 mois": "1mo", "1 an": "1y", "5 ans": "5y"}
                        historique = ticker.history(period=mapping[periode])
                        
                        if not historique.empty:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=historique.index, y=historique['Close'], mode='lines', name='Prix', line=dict(color='#00b4d8', width=2)))
                            fig.update_layout(title=f"Évolution - {nom_action}", template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)

                    with tab4:
                        st.header("📖 Lexique")
                        st.write("**PER :** Coefficient de valorisation boursière.")
                        st.write("**ROE :** Rentabilité des capitaux propres.")
                        st.write("**RSI :** Indicateur de la force des mouvements de prix.")

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")

# ====================================================================
# ONGLET PRINCIPAL 2 : ANALYSE DU MOMENTUM & VALORISATION
# ====================================================================
with onglet_principal_2:
    st.header("🚀 Suivi de l'Élan & de la Valorisation Financière")
    st.write("Ce tableau croise en direct les indicateurs techniques d'élan (RSI) et les indicateurs fondamentaux de valeur (PER).")
    
    with st.spinner("Analyse et calcul des algorithmes financiers en direct..."):
        df_momentum = obtenir_top_momentum()
        
    if not df_momentum.empty:
        st.dataframe(
            df_momentum, 
            column_config={
                "Perf. 1 An": st.column_config.TextColumn("Performance (1 an)"),
                "RSI (Force 14j)": st.column_config.ProgressColumn("RSI (Force 14j)", min_value=0, max_value=100, format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("""
        ### 💡 Comment utiliser ce tableau pour vos choix PEA ?
        Le scénario idéal pour un investisseur de type **"Value / Growth"** (Achat de croissance à prix raisonnable) est de chercher des lignes combinant :
        1. Un diagnostic d'élan **🔥 Fort & Sain** (l'action monte, elle est aimée du marché).
        2. Une évaluation financière **🟢 Sous-évalué** ou **🟡 Prix Juste** (l'action n'est pas encore trop chère par rapport à son histoire).
        
        *A contrario*, une ligne en **⚠️ Surchauffe** et **🔴 Surévalué** indique un risque important de baisse à court terme (prise de bénéfices des marchés).
        """)
    else:
        st.warning("Impossible de charger le tableau de bord.")
