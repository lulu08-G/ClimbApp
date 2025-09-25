import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

st.title("🧗 Analyseur de voies d’escalade")

uploaded_file = st.file_uploader("Upload une photo de la voie", type=["jpg", "png"])

# Charger modèle YOLO (initialement pré-entraîné sur COCO, fine-tuning possible)
model = YOLO("yolov8n.pt")  # Version mini, rapide à tester

def compute_metrics(boxes):
    nb_prises = len(boxes)
    if nb_prises < 2:
        return nb_prises, 0
    distances = []
    for i in range(len(boxes)-1):
        x1, y1, _, _ = boxes[i]
        x2, y2, _, _ = boxes[i+1]
        distances.append(np.sqrt((x2-x1)**2 + (y2-y1)**2))
    return nb_prises, np.mean(distances)

def estimate_difficulty(nb_prises, dist, devers=0):
    score = (20 - nb_prises) * 0.5 + dist * 0.2 + devers * 2
    if score < 5:
        return "V1-V2 (Facile)"
    elif score < 10:
        return "V3-V4 (Intermédiaire)"
    else:
        return "V5+ (Dur)"

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Voie uploadée", use_column_width=True)

    # Convertir PIL -> np.array pour YOLO
    img_array = np.array(image)

    # Détection des prises sans cv2
    results = model.predict(img_array)
    boxes = results[0].boxes.xywh.cpu().numpy()

    st.write(f"Nombre de prises détectées : {len(boxes)}")
    
    nb, dist = compute_metrics(boxes)
    st.write(f"Nb prises: {nb}, espacement moyen: {dist:.2f}")
    
    st.write("Difficulté estimée :", estimate_difficulty(nb, dist))
