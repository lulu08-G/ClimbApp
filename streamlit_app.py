import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from ultralytics import YOLO

st.set_page_config(layout="wide")
st.title("🧗 Analyseur de voies d’escalade")

# -------------------
# 1️⃣ Upload photo
# -------------------
uploaded_file = st.file_uploader("Upload une photo de la voie", type=["jpg", "png"])

# -------------------
# 2️⃣ Sélection couleur de voie
# -------------------
voie_couleur = st.selectbox(
    "Choisis la couleur de la voie", 
    ["Vert", "Rouge", "Bleu", "Jaune", "Autre"]
)

# -------------------
# 3️⃣ Charger modèle YOLO
# -------------------
# YOLO Tiny pré-entraîné sur COCO, pour test
model = YOLO("yolov8n.pt")  # tu peux remplacer par ton modèle finetuné

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Voie uploadée", use_column_width=True)

    # Convertir PIL -> np.array pour YOLO
    img_array = np.array(image)

    # Détection des prises
    results = model.predict(img_array)
    boxes = results[0].boxes.xywh.cpu().numpy()  # [x_center, y_center, w, h]

    st.write(f"Nombre de prises détectées : {len(boxes)}")

    # -------------------
    # 4️⃣ Dessiner les prises détectées (placeholder pour sélection future)
    # -------------------
    draw_image = image.copy()
    draw = ImageDraw.Draw(draw_image)

    for box in boxes:
        x, y, w, h = box
        # Convertir centre -> coin supérieur gauche / inférieur droit
        x1 = x - w/2
        y1 = y - h/2
        x2 = x + w/2
        y2 = y + h/2
        # Dessiner rectangle sur la prise
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    st.image(draw_image, caption="Prises détectées (placeholder)")

    # -------------------
    # 5️⃣ Placeholder pour clic sur image
    # -------------------
    st.info("À venir : clic sur les prises pour sélectionner départ / fin / voie")

