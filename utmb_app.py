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

def load_data():
    df = pd.read_excel("produits Baouw.xlsx")  # Remplace par ton fichier
    df["Marque"] = df["Marque"].astype(str) # Convertir toutes les valeurs en string
    df["Nom"] = df["Nom"].astype(str)     
    return df
df = load_data()


st.title("Profil Altimétrique de la course")

# URL brute GitHub de ton fichier GPX
gpx_url = "https://github.com/RunBooster/0003/blob/main/utmb.gpx"

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

# Chargement du GPX
try:
    points = parse_gpx_from_url(gpx_url)
    if not points:
        st.warning("Aucun point trouvé dans le fichier GPX.")
        st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement : {e}")
    st.stop()

# Calcul des distances cumulées et du dénivelé
distances = [0.0]
elevations = [points[0][2]]
cum_d+elev = [0.0]

for i in range(1, len(points)):
    prev = points[i - 1]
    curr = points[i]
    d = geodesic((prev[0], prev[1]), (curr[0], curr[1])).meters / 1000  # km
    distances.append(distances[-1] + d)
    elevations.append(curr[2])
    cum_d+elev.append(max(0, cum_d+elev[-1] + (curr[2] - prev[2]) if curr[2] > prev[2] else cum_d+elev[-1]))

# Tracé avec Plotly
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=distances,
    y=elevations,
    mode='lines',
    name='Altitude',
    hovertemplate=(
        'Distance : %{x:.2f} km<br>' +
        'Altitude : %{y:.0f} m<br>' +
        'D+ cumulé : %{customdata:.0f} m'
    ),
    customdata=[round(d, 1) for d in cum_d+elev],
    line=dict(color='green')
))

fig.update_layout(
    title="Altitude en fonction de la distance",
    xaxis_title="Distance (km)",
    yaxis_title="Altitude (m)",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

