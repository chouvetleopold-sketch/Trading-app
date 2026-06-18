import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

# --- FONCTION COMPLÉMENTAIRE : CALCUL DU RSI ---
def calculer_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=False).mean()
    ma_down = down.ewm(com=periods - 1, adjust=False).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi.iloc[-1] if not rsi.empty else 50

# --- FONCTION POUR LE MOMENTUM (ANALYSES DES LEAVERS) ---
@st.cache_data(ttl=3600) # Garde en mémoire pendant 1h pour éviter de ralentir l'application
def obtenir_top_momentum():
    # Sélection de quelques grandes actions européennes de référence éligibles PEA
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
            hist = t.history(period="1y")
            if len(hist) > 200:
                prix_actuel = hist['Close'].iloc[-1]
                prix_an_dernier = hist['Close'].iloc[0]
                perf_1an = ((prix_actuel - prix_an_dernier) / prix_an_dernier) * 100
                
                ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
                au_dessus_ma200 = "Oui 📈" if prix_actuel > ma200 else "Non 📉"
                
                rsi_actuel = calculer_rsi(hist)
                
                # Évaluation de l'élan globale
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
                    "Tendance Long Terme (MA200)": au_dessus_ma200,
                    "RSI (Force 14j)": round(rsi_actuel, 1),
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
        <p style="margin: 0 0 20px 0; font-size: 1.1rem; opacity: 0.9;">Analysez une action par son nom ou découvrez les entreprises avec le meilleur élan boursier.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# CRÉATION DES ONGLETS PRINCIPAUX (Recherche vs Découverte Globale)
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
                        st.write("**ROE :** Rentabilité de l'argent investi par les actionnaires.")
                        st.write("**RSI :** Indicateur de la force et de la vitesse des mouvements de prix.")

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")

# ====================================================================
# ONGLET PRINCIPAL 2 : ANALYSE DU MOMENTUM (NOUVEAUTÉ)
# ====================================================================
with onglet_principal_2:
    st.header("🚀 Tableau de Suivi de l'Élan Boursier (Momentum)")
    st.write("Ce tableau analyse en temps réel les indicateurs d'élan d'un panier d'actions européennes majeures éligibles au PEA.")
    
    with st.spinner("Analyse et calcul des indicateurs techniques en direct..."):
        df_momentum = obtenir_top_momentum()
        
    if not df_momentum.empty:
        # Affichage du tableau de bord propre
        st.dataframe(
            df_momentum, 
            column_config={
                "Perf. 1 An": st.column_config.TextColumn("Performance (1 an)"),
                "RSI (Force 14j)": st.column_config.ProgressColumn("RSI (Force 14j)", min_value=0, max_value=100, format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Guide d'aide à la lecture sous le tableau
        st.markdown("""
        ### 💡 Comment interpréter les points d'analyse importants ?
        * **Diagnostic '🔥 Fort & Sain' :** L'action progresse régulièrement sur 1 an, se situe au-dessus de sa moyenne long terme (MA200) et son RSI est équilibré (entre 50 et 75). C'est un élan haussier robuste.
        * **Diagnostic '⚠️ Surchauffe' :** L'action a grimpé très (ou trop) vite. Son RSI dépasse 75, ce qui montre une situation de surachat à court terme. Attention aux risques de consolidation.
        * **RSI (Relative Strength Index) :** Plus la jauge est remplie (proche de 70-100), plus la pression acheteuse est puissante. S'il tombe sous 30, l'action subit une forte baisse.
        """)
    else:
        st.warning("Impossible de charger le tableau de momentum pour le moment.")
