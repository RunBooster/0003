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
DATA_FILE = "private_user_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["prenom", "nom", "pays", "email"]).to_csv(DATA_FILE, index=False)

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

ravitos = []
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

elif race == "UTMB":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/utmb.gpx"
    ravitos = [{"nom": "Les Houches", "km": 7.8, "type": "L"},
        {"nom": "Saint-Gervais", "km": 21.5, "type": "S"},
        {"nom": "Les Contamines", "km": 31.2, "type": "S"},
        {"nom": "La Balme", "km": 39.8, "type": "S"},
        {"nom": "Les Chapieux", "km": 50.9, "type": "S"},
        {"nom": "Lac Combal", "km": 68.0, "type": "S"},
        {"nom": "Checrouit", "km": 76.8, "type": "L"},
        {"nom": "Courmayeur", "km": 81.7, "type": "A"},
        {"nom": "Bertone", "km": 87.2, "type": "L"},
        {"nom": "Arnouvaz", "km": 99.6, "type": "S"},
        {"nom": "La Fouly", "km": 115.6, "type": "S"},
        {"nom": "Champex-Lac", "km": 128.7, "type": "S"},
        {"nom": "Trient", "km": 144.3, "type": "S"},
        {"nom": "Vallorcine", "km": 155.5, "type": "S"},
        {"nom": "La Flégère", "km": 167.1, "type": "L"},
        {"nom": "Chamonix", "km": 174.3, "type": "A"}]
    tpsestime=-0.00000688788001739*(cote)*(cote)*(cote)+0.0182221182514*(cote)*(cote)-17.596971526978*(cote)+7337.2207789047
    tpsestimeCourmayeur=0.00170972442749155*(cote)*(cote)-3.31082485336002*(cote)+2134.76741108279
    tpsestimehCourmayeur=tpsestimeCourmayeur/60
    st.write('➜Estimated passage time in Courmayeur:', int(tpsestimehCourmayeur), 'h', int((tpsestimehCourmayeur%1)*60), 'min' )
    
elif race == "CCC":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/ccc.gpx"
    ravitos = [{"nom": "Bertone", "km": 13.4, "type": "S"},
        {"nom": "Arnouvaz", "km": 25.9, "type": "S"},
        {"nom": "La Fouly", "km": 40.9, "type": "S"},
        {"nom": "Champex-Lac", "km": 54.7, "type": "S"},
        {"nom": "Trient", "km": 70.3, "type": "S"},
        {"nom": "Vallorcine", "km": 81.5, "type": "S"},
        {"nom": "La Flégère", "km": 92.2, "type": "L"},
        {"nom": "Chamonix", "km": 99.0, "type": "A"}]
    tpsestime=-0.0000035772693135*(cote)*(cote)*(cote)+0.0094696502843*(cote)*(cote)-9.1536878738006*(cote)+3822.0987443797
    tpsestimeChampex=0.00110605836740463*(cote)*(cote)-2.15953926753332*(cote)+1371.82481156076
    tpsestimehChampex=tpsestimeChampex/60
    st.write('➜Estimated passage time in Champex Lac:', int(tpsestimehChampex), 'h', int((tpsestimehChampex%1)*60), 'min' )

elif race == "OCC":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/occ.gpx"
    ravitos = [{"nom": "Champex-Lac", "km": 7.6, "type": "L"},
        {"nom": "Trient", "km": 23.8, "type": "S"},
        {"nom": "Col de Balme", "km": 36.1, "type": "L"},
        {"nom": "Argentière", "km": 46.7, "type": "S"},
        {"nom": "La Flégère", "km": 51.7, "type": "L"},
        {"nom": "Chamonix", "km": 58, "type": "A"}]
    tpsestime=-0.0000018350782781*(cote)*(cote)*(cote)+0.0048352009471*(cote)*(cote)-4.6459913604367*(cote)+1925.1281152845
  
    
elif race == "TDS":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/tds.gpx"
    ravitos = [{"nom": "Checrouit", "km": 6.5, "type": "L"},
        {"nom": "Lac Combal", "km": 15.1, "type": "S"},
        {"nom": "La Thuile", "km": 35.5, "type": "S"},
        {"nom": "Seez", "km": 47.5, "type": "L"},
        {"nom": "Bourg St-Maurice", "km": 50.8, "type": "S"},
        {"nom": "Cormet de Roselend", "km": 67, "type": "S"},
        {"nom": "La Gittaz", "km": 75, "type": "L"},
        {"nom": "Beaufort", "km": 94.8, "type": "A"},
        {"nom": "Hauteluce", "km": 100.8, "type": "S"},
        {"nom": "Le Signal", "km": 116.6, "type": "S"},
        {"nom": "Les Contamines", "km": 125.5, "type": "S"},
        {"nom": "Les Houches", "km": 144.6, "type": "S"},
        {"nom": "Chamonix", "km": 152.0, "type": "A"}]
    tpsestime=-0.0000072623741683*(cote)*(cote)*(cote)+0.0183752233114*(cote)*(cote)-17.0113930227568*(cote)+6818.75621299
    tpsestimeBeaufort=0.00257053620937511*(cote)*(cote)-4.72963365166168*(cote)+2849.97700254133
    tpsestimehBeaufort=tpsestimeBeaufort/60
    st.write('➜Estimated passage time in Beaufort:', int(tpsestimehBeaufort), 'h', int((tpsestimehBeaufort%1)*60), 'min' )

elif race == "MCC":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/mcc.gpx"
    ravitos = [{"nom": "Col de la Forclaz", "km": 7.7, "type": "S"},
        {"nom": "Col de Balme", "km": 17.4, "type": "L"},
        {"nom": "Argentière", "km": 28.3, "type": "S"},
        {"nom": "Chamonix", "km": 38.5, "type": "A"}]
    tpsestime=-0.0000019286314478*(cote)*(cote)*(cote)+0.0044463631803*(cote)*(cote)-3.7343821057262*(cote)+1351.6425925073

elif race == "ETC":
    gpx_url = "https://raw.githubusercontent.com/RunBooster/0003/refs/heads/main/etc.gpx"
    ravitos = [{"nom": "La Suche", "km": 6.5, "type": "L"},
        {"nom": "Courmayeur", "km": 15, "type": "A"}]
    tpsestime=-0.0000010535438858*(cote)*(cote)*(cote)+0.0023650968191*(cote)*(cote)-1.8805758670806*(cote)+622.66999220336

tpsestimeh=tpsestime/60
st.write('➜Estimated racing time:', int(tpsestimeh), 'h', int((tpsestimeh%1)*60), 'min' )

if race != "other":
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
            if None not in (p.latitude, p.longitude, p.elevation)]
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
        cum_d_plus.append(
            max(0, cum_d_plus[-1] + (curr[2] - prev[2]) if curr[2] > prev[2] else cum_d_plus[-1]))
    # Extraire altitude exacte aux km des ravitos (approximation)
    ravito_points = []
    for r in ravitos:
        idx = min(range(len(distances)), key=lambda i: abs(distances[i] - r["km"]))
        r["altitude"] = elevations[idx]
        ravito_points.append((r["km"], elevations[idx], r["nom"]))
    # Tracer le profil
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=distances,
        y=elevations,
        name='',
        mode='lines',
        showlegend=False,
        hovertemplate=(
            'Distance : %{x:.2f} km<br>' +
            'Altitude : %{y:.0f} m<br>' +
            'Positive elevation : %{customdata:.0f} m'),
        customdata=[round(d, 1) for d in cum_d_plus],
        line=dict(color='gray')))

    # Définir les couleurs en fonction du type
    color_map = {"A": "red", "S": "green", "L": "blue"}
    fig.add_trace(go.Scatter(
        x=[r["km"] for r in ravitos],
        y=[r["altitude"] for r in ravitos],
        mode='markers+text',
        name='Aid station',
        showlegend=False,
        marker=dict(
            color=[color_map.get(r.get("type", "L")) for r in ravitos],
            size=8,
            symbol='circle'),
        text=[r["nom"] for r in ravitos],
        textposition="top center",
        hovertemplate='%{text}<br>Km : %{x:.1f}<br>Altitude : %{y:.0f} m'))

    fig.update_layout(
        title="Race profile and Aid stations",
        xaxis_title="Distance (km)",
        yaxis_title="Altitude (m)",
        hovermode="x unified",
        width=1000,
        height=500)

    st.plotly_chart(fig, use_container_width=True)
    st.write('🔴 Aid station with spare bag, 🟢 Aid station with solid food, 🔵 Aid station with drink supply only' )
    st.divider()


temp=st.checkbox("More than 20°C scheduled")
filtrer_noix = st.checkbox("Nuts intolerance")
st.divider()

values = list(range(40, 91))
Cho = st.select_slider("Your carbs consumption (g/h), or let the default value:", options=values, value=60)
typo = st.multiselect("Products you don't want", ["Bars", "Gels", "Energy Drinks", "Compotes", "Electrolytes"])
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

if com:
    new_row = pd.DataFrame([{"prenom": prenom, "nom": nom, "pays": pays, "email": email}])
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
