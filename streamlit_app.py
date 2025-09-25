import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

st.title("🧗 Analyseur de voies d’escalade")

uploaded_file = st.file_uploader("Upload une photo de la voie", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Voie uploadée")

    st.write("🚧 Détection des prises à implémenter...")
