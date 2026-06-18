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

# =================================================
