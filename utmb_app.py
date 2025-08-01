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
from collections import Counter

compteur_produits = Counter()
glucides_par_nom = {}

proposition = []

produits = "produits Baouw.xlsx"  
df = pd.read_excel(produits, sheet_name="Produits énergétiques", engine="openpyxl")
DATA_FILE = "private_user_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["prenom", "nom", "pays", "email"]).to_csv(DATA_FILE, index=False)

st.image("RunBooster.png", width=1000) 
st.divider()
langue=st.radio("Language 👇", ["English", "Français"], horizontal=True)

def load_data():
    df = pd.read_excel("produits Baouw.xlsx")  
    df["Nom"] = df["Nom"].astype(str)     
    return df
df = load_data()

race = st.selectbox("Choose your race", ("other", "UTMB", "TDS", "CCC", "OCC", "MCC", "ETC"))
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
    st.write('⌛ Estimated passage time in Courmayeur:', int(tpsestimehCourmayeur), 'h', int((tpsestimehCourmayeur%1)*60), 'min' )
    proposition.append(f"Estimated passage time in Courmayeur: {int(tpsestimehCourmayeur)}h {int((tpsestimehCourmayeur%1)*60)}min")
    
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
    st.write('⌛ Estimated passage time in Champex Lac:', int(tpsestimehChampex), 'h', int((tpsestimehChampex%1)*60), 'min' )
    proposition.append(f"Estimated passage time in Champex Lac: {int(tpsestimehChampex)}h {int((tpsestimehChampex%1)*60)}min")

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
    st.write('⌛ Estimated passage time in Beaufort:', int(tpsestimehBeaufort), 'h', int((tpsestimehBeaufort%1)*60), 'min' )
    proposition.append(f"Estimated passage time in Beaufort: {int(tpsestimehBeaufort)}h {int((tpsestimehBeaufort%1)*60)}min")

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
st.write('⏱️ Estimated racing time:', int(tpsestimeh), 'h', int((tpsestimeh%1)*60), 'min' )
proposition.append(f"Estimated racing time: {int(tpsestimeh)}h {int((tpsestimeh%1)*60)}min")

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
typo = st.multiselect("Products you don't want", ["Bars", "Gels", "Energy Drinks", "Purees", "Electrolytes"])
st.divider()

if "Bars" in typo or filtrer_noix:
    df = df[~(df["Ref"].isin(["BA", "BAS"]))]
if "Gels" in typo:
    df = df[~(df["Ref"].isin(["G"]))]
if "Energy Drinks" in typo:
    df = df[~(df["Ref"].isin(["B"]))]
if "Purees" in typo:
    df = df[~(df["Ref"].isin(["C", "CS"]))]
if "Electrolytes" in typo:
    df = df[~(df["Ref"].isin(["E"]))]
if temp:
    if race == "UTMB":
        hnosodium=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,26,27,28,29,30,31,32,33,34,35,36,37,38]
    elif race == "TDS":
        hnosodium=[0,1,2,3,4,5,6,7,8,20,21,22,23,24,25,26,27,28,29,30,31,32]
    elif race == "CCC":
        hnosodium=[11,12,13,14,15,16,17,18,19,20,21,22,23]
    else:
        hnosodium=[]
sodiumheureavant=0
plan = []
def ajuster_x(glucide, cible):
        return 1, "sachet"  # Prendre une dosette
        
heures_pleines = int(tpsestimeh)
derniere_heure = tpsestimeh % 1
produit_1 = None
ref_utilisee_precedente = None
for heure in np.arange(0, heures_pleines, 1):
    glucide_restant=Cho
    if "Energy Drinks" not in typo:
        produit_1 = df[(df["Ref"].isin(["B"]))].sample(1).iloc[0]
        glucide_1 = produit_1["Glucide"]
        x_1, unite = ajuster_x(glucide_1, 38)
        glucide_restant = Cho - (x_1 * glucide_1)

    if heure > 3 and heure % 4 == 0: #on met du salé toutes les 4 heures 
        produits_filtrés = df[(df["Ref"].isin(["CS", "BAS"]))]
        if produits_filtrés["Ref"].isin(["CS", "BAS"]).sum() == 0:  # Vérifie si produits salés sont absents
            produits_supplémentaires = df[(df["Ref"].isin(["BA", "C", "G"])) & (df["Caf"] == 0)]
            produits_filtrés = pd.concat([produits_filtrés, produits_supplémentaires])
    elif heure == 0 or heure % 5 == 0:
        produits_filtrés = df[(df["Caf"] > 1)]
        if produits_filtrés["Ref"].isin(["G", "C", "BA"]).sum() == 0:  # Vérifie si produits caféinés sont absents
            produits_filtrés = df[(df["Ref"].isin(["G", "C", "BA"]))]
    else:
        produits_filtrés = df[(df["Ref"].isin(["G", "C", "BA"])) & (df["Caf"] == 0)]

    
    produits_suivants = []
    # -- 1er produit : tiré normalement
    if not produits_filtrés.empty:
        produit_1_suiv = produits_filtrés.sample(1).iloc[0]
        produits_suivants.append(produit_1_suiv)
        glucide_restant_temp = glucide_restant - produit_1_suiv.Glucide
        est_sale = produit_1_suiv.Ref in ["CS", "BAS"]
        est_cafeine = produit_1_suiv.Caf > 1
        refs_deja_ajoutees = {produit_1_suiv.Ref}
        noms_deja_ajoutes = {produit_1_suiv.Nom}
    # -- 2e produit possible (mais selon les contraintes)
        produits_restants = produits_filtrés[~produits_filtrés["Nom"].isin(noms_deja_ajoutes)]

        while glucide_restant_temp > 10 and not produits_restants.empty:
            if est_sale:
                produits_candidats = df[(df["Ref"].isin(["G", "C", "BA"])) & (df["Caf"] == 0)]
            elif est_cafeine:
                produits_candidats = df[(df["Ref"].isin(["G", "C", "BA"])) & (df["Caf"] == 0)]
            else:
                produits_candidats = produits_restants[~produits_restants["Ref"].isin(refs_deja_ajoutees)]
            if produits_candidats.empty:
                break
            nouveau_produit = produits_candidats.sample(1).iloc[0]
            produits_suivants.append(nouveau_produit)
            glucide_restant_temp -= nouveau_produit.Glucide
            noms_deja_ajoutes.add(nouveau_produit.Nom)
            refs_deja_ajoutees.add(nouveau_produit.Ref)
           
    produits_text = []
    glucide_tot=0
    sodium_tot=0
    caf_tot=0
    
    for produit in produits_suivants:
        if glucide_restant <= 0:
            break
        if produit.Glucide <= glucide_restant+10:
            produits_text.append(f"+ 1 {produit.Nom}")
            compteur_produits[produit.Nom] += 1
            glucides_par_nom[produit.Nom] = produit.Glucide
            glucide_restant -= produit.Glucide
            glucide_tot+=produit.Glucide
            sodium_tot+=produit.Sodium
            caf_tot+=produit.Caf
            
    if temp and heure not in hnosodium and sodiumheureavant*1000 < 500 and not est_sale and "Electrolytes" not in typo:
        produit = df[(df["Ref"].isin(["E"]))].sample(1).iloc[0]
        produits_text.append(f"+ 1 tab of {produit.Nom}")
        glucide_tot+=produit.Glucide
        sodium_tot+=produit.Sodium
        compteur_produits[produit.Nom] += 1
        
    if "Energy Drinks" not in typo:
        x_brut = (Cho - glucide_tot) / glucide_1
        valeurs_possibles = [0.5, 1, 1.5]
        x_1 = min(valeurs_possibles, key=lambda x: abs(x - x_brut))
        compteur_produits[produit_1.Nom] += x_1
        glucides_par_nom[produit_1.Nom] = produit_1.Glucide
        glucide_tot+=produit_1.Glucide*x_1
        sodium_tot+=produit_1.Sodium*x_1
        caf_tot+=produit_1.Caf*x_1
        plan.append(f"🕐 Hour {heure} (Carbs: {int(glucide_tot)}g, Sodium: {int(sodium_tot*1000)}mg, Caffeine: {int(caf_tot)}mg): {x_1} scoop of {produit_1['Nom']} in water {' '.join(produits_text)}.")
    else:
        plan.append(f"🕐 Hour {heure} (Carbs: {int(glucide_tot)}g, Sodium: {int(sodium_tot*1000)}mg, Caffeine: {int(caf_tot)}mg): {' '.join(produits_text)}.")
    sodiumheureavant=sodium_tot
    if len(produits_suivants) > 0:
            ref_utilisee_precedente = produits_suivants[0].Ref
        
if derniere_heure > 0:
    glucide_tot=0
    sodium_tot=0
    caf_tot=0
    glucide_restant = (Cho * derniere_heure)
    if "Energy Drinks" not in typo:
        produit_1 = df[df["Ref"] == "B"].sample(1).iloc[0]
        glucide_1 = produit_1["Glucide"]
        x_brut = (Cho*derniere_heure) / glucide_1
        valeurs_possibles = [0.5, 1, 1.5]
        x_1 = min(valeurs_possibles, key=lambda x: abs(x - x_brut))
        compteur_produits[produit_1.Nom] += x_1
        glucides_par_nom[produit_1.Nom] = produit_1.Glucide
        glucide_tot+=produit_1.Glucide*x_1
        sodium_tot+=produit_1.Sodium*x_1
        caf_tot+=produit_1.Caf*x_1
        glucide_restant = (Cho * derniere_heure) - (x_1 * glucide_1)
    produits_suivants = df[(df["Ref"].isin(["G", "C", "BA"]))].sample(2)
    
    produits_text = []
    for produit in produits_suivants.itertuples():
        if glucide_restant <= 0:
            break
        if produit.Glucide <= glucide_restant:
            produits_text.append(f"+ 1 {produit.Nom}")
            compteur_produits[produit.Nom] += 1
            glucides_par_nom[produit.Nom] = produit.Glucide
            glucide_restant -= produit.Glucide
            glucide_tot+=produit.Glucide
            sodium_tot+=produit.Sodium*1000
            caf_tot+=produit.Caf
    if "Energy Drinks" not in typo:    
        plan.append(f"🕐 Last hour (Carbs: {int(glucide_tot)}g, Sodium: {int(sodium_tot)}mg, Caffeine: {int(caf_tot)}mg) : {x_1} scoop of {produit_1['Nom']} in water {', '.join(produits_text)}.")
    else:
        plan.append(f"🕐 Last hour (Carbs: {int(glucide_tot)}g, Sodium: {int(sodium_tot)}mg, Caffeine: {int(caf_tot)}mg) : {', '.join(produits_text)}.")

     


col4, col5, col6 = st.columns([1,1,1])
with col4:
    prenom = st.text_input("First name")
with col5:
    nom = st.text_input("Last name")
with col6:
    pays = st.text_input("Country")
email = st.text_input("E-mail")
com = st.checkbox("I agree to receive Baouw and RunBooster offers")

if st.button("Submit"):
    #new_row = pd.DataFrame([{"prenom": prenom, "nom": nom, "pays": pays, "email": email}])
    #df = pd.read_csv(DATA_FILE)
    #df = pd.concat([df, new_row], ignore_index=True)
    #df.to_csv(DATA_FILE, index=False)
    resume_text = []
    for nom, count in compteur_produits.items():
        glucide_unitaire = glucides_par_nom.get(nom, 0)
        if nom == "Drink Mix":
            total_glucides = round(count * glucide_unitaire)
            resume_text.append(f"{total_glucides} g of {nom}")
        elif nom == "Electrolytes":
            total = round(count) if count % 1 == 0 else round(count, 1)
            resume_text.append(f"{total} tabs of {nom}")
        else:
            total = round(count) if count % 1 == 0 else round(count, 1)
            resume_text.append(f"{total} × {nom}")
    #plan.append("\n### 🧾 To take:\n" + "\n".join([f"• {ligne}" for ligne in resume_text]))
    
    
    if plan:
         st.write("### Nutritional plan generated :")
         for ligne in proposition:
              st.write(ligne)
         for ligne in plan:
              st.write(ligne)
    texte = "### 🧾 To take:\n" + "".join([f"• {ligne}<br>" for ligne in resume_text])
    st.markdown(texte, unsafe_allow_html=True)
    
    #for bloc in plan:
        #st.markdown(f"### Heure {bloc['heure']} (Total Glucides : {bloc['glucides']}g)")
        #for p in bloc['produits']:
            #st.markdown(f"- {p['Nom']} | Ref: {p['Ref']} | Glucides: {p['Glucide']}g | Caf: {p['Caf']}")
