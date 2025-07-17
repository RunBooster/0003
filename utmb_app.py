import streamlit as st
import pandas as pd
import random
import smtplib
import numpy as np
from fpdf import FPDF
import os
from email.message import EmailMessage

produits = "produits.xlsx"  
df = pd.read_excel(produits, sheet_name="Produits énergétiques", engine="openpyxl")

left, middle =st.columns([1,3], vertical_alignment="bottom")
left.image("RunBooster(1).png", width=100) 
middle.subheader("Boost ton run grâce à une alimentation controlée")
st.divider()

def load_data():
    df = pd.read_excel("produits.xlsx")  # Remplace par ton fichier
    df["Marque"] = df["Marque"].astype(str) # Convertir toutes les valeurs en string
    df["Nom"] = df["Nom"].astype(str)     
    return df
df = load_data()
