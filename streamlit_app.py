import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuration de la page
st.set_page_config(page_title="Tableau de Bord PEA", layout="wide")

# --- BLOC AJOUTÉ : BANDEAU VERT CACA D'OIE EN HAUT ---
st.markdown(
    """
    <div style="background-color: #6B6B2F; padding: 20px; border-radius: 5px; margin-bottom: 25px; text-align: center;">
        <h1 style="color: white; margin: 0; font-family: sans-serif;">📈 ESPACE D'ANALYSE PEA</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

st.title("Mon Tableau de Bord PEA Professionnel")
st.write("Sélectionnez une action pour analyser sa santé financière, sa valorisation et ses graphiques de tendance.")

# Liste complète des 120 actions du SBF 120
liste_actions = [
    "AC.PA", "ACA.PA", "AI.PA", "AIR.PA", "ALD.PA", "ALO.PA", "ALT.PA", "AMUN.PA", "ATE.PA",
    "ATO.PA", "BALO.PA", "BAM.PA", "BBO.PA", "BCP.PA", "BEN.PA", "BIM.PA", "BNP.PA", "BOLL.PA", "BOUY.PA",
    "CAFP.PA", "CAP.PA", "CARA.PA", "CARR.PA", "CDI.PA", "CEG.PA", "CHG.PA", "CIE.PA", "COFA.PA", "COV.PA",
    "CS.PA", "DBV.PA", "DEC.PA", "DERI.PA", "DFV.PA", "DG.PA", "DIM.PA", "DSY.PA", "EDEN.PA", "EDF.PA",
    "EN.PA", "ENGI.PA", "ERA.PA", "ERI.PA", "ETL.PA", "EURA.PA", "EVO.PA", "FDJ.PA", "FR.PA", "FTI.PA",
    "GFC.PA", "GLE.PA", "GTT.PA", "HO.PA", "ICAD.PA",
