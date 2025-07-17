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

uploaded_file = "utmb.gpx"
def calculate_slope_gradient(elev1, elev2, dist):
    if dist < 1:
        return 0
    return (elev2 - elev1) / dist * 100.0

if uploaded_file is not None and uploaded_file.name.endswith(".gpx"):
    try:
        gpx = gpxpy.parse(uploaded_file)
        points = [
            (p.latitude, p.longitude, p.elevation)
            for trk in gpx.tracks
            for seg in trk.segments
            for p in seg.points
            if None not in (p.latitude, p.longitude, p.elevation)
        ]
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier GPX : {e}")
        points = []


    if len(points) < 2:
        st.warning("Pas assez de points pour effectuer l'analyse.")
    else:

        distances = [0]
        elevations = [points[0][2]]
        for i in range(1, len(points)):
            d = geodesic((points[i-1][0], points[i-1][1]), (points[i][0], points[i][1])).meters
            distances.append(distances[-1] + d)
            elevations.append(points[i][2])

        MIN_DISTANCE = 250
        MIN_ELEVATION_GAIN = 10
        MIN_DESC_ELEVATION = -10
        MIN_GRADE = 2.9
        MIN_DESC_GRADE = -2.9

        def detect_segments(elev_condition):
            segments = []
            current = {"start": None, "end": None, "distance": 0, "elevation": 0}
            for i in range(1, len(distances)):
                dist = distances[i] - distances[i-1]
                elev = elevations[i] - elevations[i-1]
                grade = calculate_slope_gradient(elevations[i-1], elevations[i], dist)

                if elev_condition(grade):
                    if current["start"] is None:
                        current["start"] = i - 1
                    current["end"] = i
                    current["distance"] += dist
                    current["elevation"] += elev
                elif current["start"] is not None:
                    segments.append(current.copy())
                    current = {"start": None, "end": None, "distance": 0, "elevation": 0}
            if current["start"] is not None:
                segments.append(current)
            return segments

        def merge_segments(segments):
            merged = []
            for s in segments:
                if not merged:
                    merged.append(s)
                else:
                    last = merged[-1]
                    gap = distances[s["start"]] - distances[last["end"]]
                    if gap <= 50:
                        last["end"] = s["end"]
                        last["distance"] += s["distance"] + gap
                        last["elevation"] += s["elevation"]
                    else:
                        merged.append(s)
            return merged

        def finalize_segments(segments, is_ascent=True):
            results = []
            for s in segments:
                if abs(s["distance"]) >= MIN_DISTANCE and abs(s["elevation"]) >= (MIN_ELEVATION_GAIN if is_ascent else abs(MIN_DESC_ELEVATION)):
                    grades = [
                        calculate_slope_gradient(elevations[i-1], elevations[i], distances[i] - distances[i-1])
                        for i in range(s["start"]+1, s["end"]+1)
                        if (distances[i] - distances[i-1]) >= 5
                    ]
                    avg_grade = sum(grades) / len(grades) if grades else 0
                    max_grade = max([
                        g for i, g in enumerate(grades)
                        if i+1 < len(grades) and abs(g) < 35
                    ], default=0)
                    difficulty = (avg_grade ** 2) * (s["distance"] / 1000)

                    results.append({
                        "Début (km)": distances[s["start"]] / 1000,
                        "Fin (km)": distances[s["end"]] / 1000,
                        "Distance (m)": distances[s["end"]] - distances[s["start"]],
                        "D+ (m)": abs(s["elevation"]) if is_ascent else None,
                        "D- (m)": abs(s["elevation"]) if not is_ascent else None,
                        "% moyen": avg_grade,
                        "% max": max_grade,
                        "Difficulté": difficulty,
                        "Type": "Montée" if is_ascent else "Descente"
                    })
            return results

        climbs = finalize_segments(
            merge_segments(detect_segments(lambda g: g >= MIN_GRADE)),
            is_ascent=True
        )
        descents = finalize_segments(
            merge_segments(detect_segments(lambda g: g <= MIN_DESC_GRADE)),
            is_ascent=False
        )

        df = pd.DataFrame(climbs + descents)
        df = df.sort_values(by="Début (km)").reset_index(drop=True)

        if df.empty:
            st.info("Aucune montée ou descente détectée avec les critères appliqués.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.array(distances)/1000, y=elevations,
                                    mode='lines', line=dict(color='lightgray'), name='Profil'))
            for _, row in df.iterrows():
                s = min(range(len(distances)), key=lambda i: abs(distances[i]/1000 - row["Début (km)"]))
                e = min(range(len(distances)), key=lambda i: abs(distances[i]/1000 - row["Fin (km)"]))
                difficulty = row.get("Difficulté", 0) or 0
                color = f"rgba(0, 0, 255, {min(1, difficulty/1000):.2f})" if row["Type"] == "Descente" else f"rgba(255, 0, 0, {min(1, difficulty/1000):.2f})"
                hovertext = (
                    f"{row['Type']}<br>"
                    f"Distance: {row['Distance (m)']:.0f} m<br>"
                    f"% moyen: {row['% moyen']:.1f}%<br>"
                    f"% max: {row['% max']:.1f}%<br>"
                    f"D+: {row.get('D+ (m)', '-'):.1f} m<br>"
                    f"D-: {row.get('D- (m)', '-'):.1f} m<br>"
                    f"Difficulté: {row['Difficulté']:.1f}"
                )
                fig.add_trace(go.Scatter(
                    x=np.array(distances[s:e+1])/1000,
                    y=elevations[s:e+1],
                    mode='lines+markers',
                    line=dict(width=3, color=color),
                    name=f"{row['Type']}",
                    hoverinfo='text',
                    text=[hovertext] * (e - s + 1)
                ))
            fig.update_layout(title="Profil altimétrique", xaxis_title="Distance (km)", yaxis_title="Altitude (m)", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📊 Statistiques globales")
            # Calcul du pourcentage de pente global pondéré
            total_distance = sum(df["Distance (m)"])
            weighted_grade_sum = sum(df["% moyen"] * df["Distance (m)"])
            global_grade = weighted_grade_sum / total_distance if total_distance > 0 else 0
            
            top_climbs = df[df["Type"] == "Montée"].sort_values(by="Difficulté", ascending=False).head(5)
            top_descents = df[df["Type"] == "Descente"].sort_values(by="Difficulté", ascending=False).head(5)

            st.markdown("Voici les **5 principales montées** (les plus longues) :")
            for _, row in top_climbs.iterrows():
                st.markdown(f"- De {row['Début (km)']:.1f} km à {row['Fin (km)']:.1f} km : {row['Distance (m)']:.0f} m, pente moyenne {row['% moyen']:.1f}")

            st.markdown("Voici les **5 principales descentes** (les plus longues) :")
            for _, row in top_descents.iterrows():
                st.markdown(f"- De {row['Début (km)']:.1f} km à {row['Fin (km)']:.1f} km : {row['Distance (m)']:.0f} m, pente moyenne {row['% moyen']:.1f}")


            st.markdown("""
                <div style='background-color:#cc0000; color:white; border-radius:6px; padding:8px; border-left:5px solid red; font-weight:bold;'>🚵‍♀️ Montée la plus difficile</div>
            """, unsafe_allow_html=True)

            st.write(df[(df['Type'] == 'Montée') & (df['Difficulté'] == df[df['Type'] == 'Montée']['Difficulté'].max())].iloc[[0]].drop(columns=["Difficulté"]))

            st.markdown("""
                <div style='background-color:#990000; color:white; border-radius:6px; padding:8px; border-left:5px solid red; font-weight:bold;'>📈 Pente maximale en montée</div>
            """, unsafe_allow_html=True)

            st.write(df[(df['Type'] == 'Montée') & (df['% max'] == df[df['Type'] == 'Montée']['% max'].max())].iloc[[0]].drop(columns=["Difficulté"]))

            st.markdown("""
                <div style='background-color:#003399; color:white; border-radius:6px; padding:8px; border-left:5px solid blue; font-weight:bold;'>🏔️ Descente la plus difficile</div>
            """, unsafe_allow_html=True)

            st.write(df[(df['Type'] == 'Descente') & (df['Difficulté'] == df[df['Type'] == 'Descente']['Difficulté'].max())].iloc[[0]].drop(columns=["Difficulté"]))

            st.markdown("""
                <div style='background-color:#003399; color:white; border-radius:6px; padding:8px; border-left:5px solid blue; font-weight:bold;'>📉 Pente maximale en descente</div>
            """, unsafe_allow_html=True)

            st.write(df[(df['Type'] == 'Descente') & (df['% max'] == df[df['Type'] == 'Descente']['% max'].min())].iloc[[0]].drop(columns=["Difficulté"]))


            st.subheader("📊 Statistiques globales")
            top_segments = df.sort_values(by="Difficulté", ascending=False).head(5)
            top_segments["% moyen"] = top_segments["% moyen"].abs()
            top_total = top_segments["Distance (m)"].sum()
            # Filtrer uniquement les montées pour ce calcul
            df_climbs = df[df["Type"] == "Montée"].copy()

            # Éviter division par zéro
            if not df_climbs.empty:
                # Crée une pondération basée sur difficulté × distance × D+
                df_climbs["poids"] = df_climbs["Difficulté"] * df_climbs["Distance (m)"] * df_climbs["D+ (m)"].fillna(0)
                total_poids = df_climbs["poids"].sum()
                
                if total_poids > 0:
                    global_grade = (df_climbs["% moyen"] * df_climbs["poids"]).sum() / total_poids
                else:
                    global_grade = 0
            else:
                global_grade = 0


            total_distance_km = distances[-1] / 1000 if distances else 0
            total_dplus = df["D+ (m)"].sum()
            dplus_per_km = total_dplus / total_distance_km if total_distance_km > 0 else 0

        

            # Bloc d'affichage visuel stylé pour les statistiques globales
            st.markdown(f"""
            <div style='
                border: 2px dotted #aaa; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 25px 0;
                background-color: rgba(30, 30, 60, 0.85);
                color: white;'>

            <h4 style='text-align:center;'>📊 Statistiques globales de la course</h4>

            <div style='
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 6px; 
                text-align: center; 
                font-size: 18px; 
                margin-bottom: 10px;'>
                <strong>D+ total :</strong> {total_dplus:.0f} m
            </div>

            <div style='
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 6px; 
                text-align: center; 
                font-size: 18px; 
                margin-bottom: 10px;'>
                <strong>Distance totale :</strong> {total_distance_km:.1f} km
            </div>

            <div style='
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 6px; 
                text-align: center; 
                font-size: 18px; 
                margin-bottom: 10px;'>
                <strong>Ratio D+ par kilomètre :</strong> {dplus_per_km:.1f} m/km
            </div>

            <div style='
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 6px; 
                text-align: center; 
                font-size: 18px; 
                margin-bottom: 10px;'>
                <strong>Pente moyenne pondérée (en prenant les principales montées) :</strong> {global_grade:.1f}%
            </div>

            <hr style='margin: 20px 0; border: 1px solid #999;' />

            <h4 style='text-align:center;'>⚖️ Analyse spectre force-vitesse</h4>

            <div style='
                border: 1px solid #999; 
                background-color: rgba(240, 240, 240, 0.2); 
                padding: 12px; 
                border-radius: 6px; 
                font-size: 16px;
                color: white;'>
                {"🟥 Ce parcours est très orienté force." if dplus_per_km > 58 else "🟧 Ce parcours est orienté force-vitesse." if 30 < dplus_per_km <= 58 else "🟩 Ce parcours est plutôt orienté vitesse."}
            </div>
            </div>
            """, unsafe_allow_html=True)
