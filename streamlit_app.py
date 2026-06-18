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

# --- FONCTION POUR LE MOMENTUM ET LA VALORISATION ---
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
                
                # Calcul de la valorisation
                per_actuel = info.get("trailingPE", None)
                per_moyen_5ans = info.get("fiveYearAvgTrailingPE", None)
                
                if per_actuel and per_moyen_5ans:
                    ratio_val = per_actuel / per_moyen_5ans
                    if ratio_val < 0.85: evaluation = "🟢 Sous-évalué (Décote)"
                    elif ratio_val > 1.15: evaluation = "🔴 Surévalué (Cher)"
                    else: evaluation = "🟡 Prix Juste"
                elif per_actuel:
                    if per_actuel < 13: evaluation = "🟢 Sous-évalué (PER bas)"
                    elif per_actuel > 25: evaluation = "🔴 Surévalué (PER haut)"
                    else: evaluation = "🟡 Prix Juste"
                else:
                    evaluation = "📊 N/A"
                
                # Diagnostic d'élan
                if perf_1an > 10 and prix_actuel > ma200 and 50 <= rsi_actuel <= 75: elan = "🔥 Fort & Sain"
                elif perf_1an > 20 and rsi_actuel > 75: elan = "⚠️ Surchauffe"
                elif perf_1an < 0: elan = "❄️ Baissier"
                else: elan = "⚖️ Neutre"
                
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
        <p style="margin: 0 0 20px 0; font-size: 1.1rem; opacity: 0.9;">Prenez des décisions éclairées pour votre PEA grâce aux indicateurs fondamentaux et techniques.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# REORGANISATION : LE LEXIQUE PASSE EN ONGLET PRINCIPAL TOUT EN HAUT
onglet_principal_1, onglet_principal_2, onglet_principal_3 = st.tabs([
    "🔍 Rechercher une entreprise", 
    "🚀 Découverte & Momentum Européen", 
    "📖 Lexique Financier"
])

# ====================================================================
# ONGLET PRINCIPAL 1 : MOTEUR DE RECHERCHE
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
                    
                    # Plus que 3 sous-onglets ici (Le lexique a bougé !)
                    tab1, tab2, tab3 = st.tabs(["🏢 Présentation & Actu", "📈 Analyse Financière", "📊 Graphiques Évolution"])
                    
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

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")

# ====================================================================
# ONGLET PRINCIPAL 2 : MOMENTUM
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
    else:
        st.warning("Impossible de charger le tableau de bord.")

# ====================================================================
# ONGLET PRINCIPAL 3 : LEXIQUE FINANCIER GLOBAL (DEPLACÉ ICI)
# ====================================================================
with onglet_principal_3:
    st.header("📖 Lexique pour comprendre les indicateurs")
    st.write("Retrouvez ici les définitions simples de toutes les mesures utilisées dans l'application :")
    st.markdown("---")
    
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
    st.write("Une marge de 15% signifie que sur 100€ de ventes, il reste 15€ de pur profit dans les caisses de l'entreprise une fois toutes les factures payées.")
    
    st.subheader("🔹 Price-to-Sales (PSR)")
    st.write("**Ce que c'est :** Le ratio Cours / Chiffre d'Affaires.")
    st.write("Il compare la valeur de l'entreprise à ses ventes totales. Un PSR inférieur à 1 ou 2 est souvent considéré comme intéressant. Très utile pour analyser des sociétés en forte croissance qui n'ont pas encore de gros bénéfices nets.")
    
    st.subheader("🔹 Capitalisation Boursière")
    st.write("**Ce que c'est :** La valeur totale de l'entreprise sur le marché.")
    st.write("C'est le prix global qu'il faudrait payer pour acheter 100% de l'entreprise aujourd'hui (calculé en multipliant le nombre total d'actions par le prix d'une action). Elle s'exprime en Millions (M €) ou Milliards (Md €).")
    
    st.subheader("🔹 Bêta (Volatilité)")
    st.write("**Ce que c'est :** L'indicateur de nervosité de l'action par rapport au marché général.")
    st.write("Le marché de référence a un Bêta de 1. Si l'action a un Bêta de 1.5, elle est plus réactive : si le marché monte de 10%, elle aura tendance à monter de 15%. Si elle a un Bêta de 0.6, elle est très calme.")

    st.subheader("🔹 RSI (Relative Strength Index)")
    st.write("**Ce que c'est :** Un indicateur technique qui mesure la vitesse et la force des mouvements de prix à court terme.")
    st.write("Le RSI oscille entre 0 et 100. Un RSI supérieur à 70 indique généralement que l'action est en zone de surachat (l'élan est très fort mais attention au risque de baisse). Un RSI inférieur à 30 indique une zone de survente.")
