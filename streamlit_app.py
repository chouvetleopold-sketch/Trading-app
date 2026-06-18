import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

# --- BLOC : GRAND BANDEAU GLOBAL EN COULEUR ---
st.markdown(
    """
    <div style="background-color: #6B6B2F; padding: 30px; border-radius: 8px; margin-bottom: 20px; color: white; font-family: sans-serif;">
        <h1 style="color: white; margin: 0 0 10px 0; font-size: 2.5rem;">📉 Mon Grand Moteur de Recherche Boursier</h1>
        <p style="margin: 0 0 20px 0; font-size: 1.1rem; opacity: 0.9;">Entrez le code de n'importe quelle action mondiale ou européenne pour analyser ses indicateurs en temps réel.</p>
        <p style="margin: 0 0 5px 0; font-weight: bold; font-size: 1rem;">Entrez le symbole Yahoo Finance de l'entreprise :</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Zone de saisie de texte libre (LVMH 'MC.PA' par défaut)
choix = st.text_input("", value="MC.PA", label_visibility="collapsed").strip().upper()

# Guide d'aide pour l'utilisateur sous la barre de recherche
st.caption("💡 *Exemples de codes à taper : **MC.PA** (LVMH), **TTE.PA** (Total), **STMMI.MI** (STMicroelectronics), **AIR.DE** (Airbus), **ASML.AS** (ASML)*")

st.markdown("<br>", unsafe_allow_html=True)

if choix:
    try:
        ticker = yf.Ticker(choix)
        info = ticker.info
        
        # LIGNE CORRIGÉE : Vérification robuste de l'existence du symbole
        if not info or not any(k in info for k in ['regularMarketPrice', 'currentPrice', 'previousClose', 'longName']):
            st.error(f"❌ Le symbole boursier '{choix}' semble incorrect ou n'existe pas sur Yahoo Finance. Vérifiez le suffixe (ex: .PA, .MI, .DE).")
        else:
            # Nom de l'action pour l'affichage
            nom_action = info.get('longName', choix)
            
            tab1, tab2, tab3, tab4 = st.tabs(["🏢 Présentation & Actu", "📈 Analyse Financière", "📊 Graphiques Évolution", "📖 Lexique"])
            
            # 1. ONGLET PRÉSENTATION
            with tab1:
                st.header(f"🏢 À propos de {nom_action}")
                description = info.get("longBusinessSummary", "Aucune description disponible pour cette action.")
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

            # 2. ONGLET ANALYSE FINANCIÈRE
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
                if market_cap and market_cap >= 1000000000:
                    market_cap_txt = str(round(market_cap / 1000000000, 2)) + " Md €"
                elif market_cap:
                    market_cap_txt = str(round(market_cap / 1000000, 2)) + " M €"
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
                col7.metric("Capitalisation Boursière", market_cap_txt)
                col8.metric("Bêta (Volatilité)", f"{beta} (Marché = 1)")

            # 3. ONGLET GRAPHANALYSE
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
                    fig.add_trace(go.Scatter(x=historique.index, y=historique['Close'], mode='lines', name='Prix de Clôture', line=dict(color='#00b4d8', width=2)))
                    
                    if historique['MA200'].notna().any():
                        fig.add_trace(go.Scatter(x=historique.index, y=historique['MA200'], mode='lines', name='Moyenne Mobile 200 jours', line=dict(color='#ff4d6d', width=1.5, dash='dash')))
                    
                    fig.update_layout(title=f"Évolution du cours - {nom_action}", xaxis_title="Date", yaxis_title="Prix", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("Impossible de charger les données graphiques pour ce symbole.")

            # 4. ONGLET LEXIQUE
            with tab4:
                st.header("📖 Lexique pour comprendre les indicateurs")
                st.write("Retrouvez ici les définitions simples de toutes les mesures affichées.")
                
                st.subheader("🔹 PER (Price Earnings Ratio)")
                st.write("Il indique combien de fois vous payez le bénéfice de l'entreprise. Un PER de 15 signifie que l'action s'achète 15 fois son bénéfice annuel.")
                
                st.subheader("🔹 ROE (Return on Equity)")
                st.write("Mesure l'efficacité avec laquelle l'entreprise utilise l'argent de ses actionnaires pour créer des bénéfices. Un bon ROE dépasse généralement 12-15%.")
                
                st.subheader("🔹 Rendement du Dividende")
                st.write("Le pourcentage du prix actuel reversé en cash aux actionnaires. Idéal pour générer des rentes passives au sein de l'enveloppe fiscale du PEA.")
                
                st.subheader("🔹 Capitalisation Boursière")
                st.write("Le prix total pour acquérir 100% de l'entreprise sur le marché (exprimé en Millions ou Milliards d'Euros).")

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la recherche : {e}")
