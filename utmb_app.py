import streamlit as st
import pandas as pd
import random
import smtplib
import numpy as np
from fpdf import FPDF
import os
from email.message import EmailMessage
from scipy.optimize import curve_fit
import plotly.graph_objs as go
import gpxpy
from geopy.distance import geodesic
import requests

produits = "produits Baouw.xlsx"  
df = pd.read_excel(produits, sheet_name="Produits énergétiques", engine="openpyxl")


st.image("RunBooster.png", width=1000) 
st.divider()
langue=st.radio("Language 👇", ["English", "Français"], horizontal=True)

def load_data():
    df = pd.read_excel("produits Baouw.xlsx")  # Remplace par ton fichier
    df["Marque"] = df["Marque"].astype(str) # Convertir toutes les valeurs en string
    df["Nom"] = df["Nom"].astype(str)     
    return df
df = load_data()

race = st.selectbox("Choose your race", ("UTMB", "TDS", "CCC", "OCC", "MCC", "ETC", "other"))
cote = st.number_input("Your UTMB Index", min_value=1, value=500)


if race == "other":
    valid_index = st.checkbox("I entered a valid UTMB Index")
    if valid_index:
        distance = st.number_input("Your distance in km", format="%0.1f")
        deniv = st.number_input("Your positive elevation m", format="%0f")
        disteff=(distance+(deniv/100))
        tpsestime=1000*(0.00000006964734390393*(disteff)*(disteff)*(disteff)*(disteff)-0.00006550491191697*(disteff)*(disteff)*(disteff)+0.020181800970007*(disteff)*(disteff)+2.20983621768921*(disteff))/cote
    else:
        st.write("Your estimated time 👇")
        tpsh=st.number_input("Hours", min_value=0)
        tpsm=st.number_input("Minutes", min_value=0, max_value=59)
        tpsestime=(tpsh*60)+tpsm



if race == "UTMB":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/utmb.gpx"
    ravitos = [
        {"nom": "Les Houches", "km": 7.8},
        {"nom": "Saint-Gervais", "km": 21.5},
        {"nom": "Les Contamines", "km": 31.2},
        {"nom": "La Balme", "km": 39.8},
        {"nom": "Les Chapieux", "km": 50.9},
        {"nom": "Lac Combal", "km": 68.0},
        {"nom": "Checrouit", "km": 77.6},
        {"nom": "Courmayeur", "km": 80.2},
        {"nom": "Bertone", "km": 85.2},
        {"nom": "Arnouvaz", "km": 97.4},
        {"nom": "La Fouly", "km": 115.6},
        {"nom": "Champex-Lac", "km": 127.2},
        {"nom": "Trient", "km": 141.3},
        {"nom": "Vallorcine", "km": 151.8},
        {"nom": "La Flégère", "km": 159.5},
        {"nom": "Chamonix (Arrivée)", "km": 170.0}
    ]

@st.cache_data
def parse_gpx_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    gpx = gpxpy.parse(response.text)

    points = [
        (p.latitude, p.longitude, p.elevation)
        for trk in gpx.tracks
        for seg in trk.segments
        for p in seg.points
        if None not in (p.latitude, p.longitude, p.elevation)
    ]
    return points

try:
    points = parse_gpx_from_url(gpx_url)
    if not points:
        st.warning("Aucun point trouvé dans le fichier GPX.")
        st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement : {e}")
    st.stop()

# Calcul des distances et dénivelé
distances = [0.0]
elevations = [points[0][2]]
cum_d_plus = [0.0]

for i in range(1, len(points)):
    prev = points[i - 1]
    curr = points[i]
    d = geodesic((prev[0], prev[1]), (curr[0], curr[1])).meters / 1000
    distances.append(distances[-1] + d)
    elevations.append(curr[2])
    cum_d_plus.append(max(0, cum_d_plus[-1] + (curr[2] - prev[2]) if curr[2] > prev[2] else cum_d_plus[-1]))

# Extraire altitude exacte aux km des ravitos (approximation)
ravito_points = []
for r in ravitos:
    # Chercher l’index du point le plus proche de la distance
    idx = min(range(len(distances)), key=lambda i: abs(distances[i] - r["km"]))
    r["altitude"] = elevations[idx]
    ravito_points.append((r["km"], elevations[idx], r["nom"]))

# Tracer le profil
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=distances, y=elevations, name='', mode='lines', showlegend=False,  # <-- ceci supprime la légende
    hovertemplate=(
        'Distance : %{x:.2f} km<br>' +
        'Altitude : %{y:.0f} m<br>' +
        'D+ cumulé : %{customdata:.0f} m'), customdata=[round(d, 1) for d in cum_d_plus], line=dict(color='gray')))

# Ajouter les ravitos comme scatter avec annotations
fig.add_trace(go.Scatter(x=[r[0] for r in ravito_points], y=[r[1] for r in ravito_points], mode='markers+text', name='Aid Station',
    showlegend=False,  # <-- ceci supprime la légende
    marker=dict(color='blue', size=8, symbol='circle'), text=[r[2] for r in ravito_points], textposition="top center", hovertemplate='%{text}<br>Km : %{x:.1f}<br>Altitude : %{y:.0f} m'))

fig.update_layout(title="Race profile and Aid stations", xaxis_title="Distance (km)", yaxis_title="Altitude (m)",
    hovermode="x unified", width=1000, height=500)
st.plotly_chart(fig, use_container_width=True)

temp=st.checkbox("More than 20°C scheduled?")

col0, col1, col2, col3 = st.columns([0.5, 0.5, 0.5, 1.8])  
with col0:
    st.write("Intolérances ?")
with col1:
    filtrer_noix = st.checkbox("Nuts")
with col2:
    filtrer_lactose = st.checkbox("Lactose")
with col3:
    filtrer_gluten = st.checkbox("Gluten")
    
st.divider()

col4, col5, col6 = st.columns([1,1,1])
with col4:
    prenom = st.text_input("First name")
with col5:
    nom = st.text_input("Last name")
with col6:
    pays = st.text_input("Country")
email = st.text_input("E-mail")
com = st.checkbox("I agree to receive Baouw and RunBooster offers")

