# streamlit_app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import base64
from datetime import datetime, time

st.set_page_config(page_title="CoTeamer Dofus", layout="wide",
                   page_icon="🟢")

# ---------------------------
# Helpers
# ---------------------------
def make_class_image(name, size=(300,300), bg=(10,80,20)):
    """Génère une vignette simple pour une classe (texte centré)."""
    img = Image.new("RGB", size, color=bg)
    draw = ImageDraw.Draw(img)
    # Attempt to load a default font; fallback
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    w,h = draw.textsize(name, font=font)
    draw.text(((size[0]-w)/2,(size[1]-h)/2), name, fill=(230,255,200), font=font)
    return img

def image_to_bytes(img: Image.Image):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def export_profiles_csv(profiles):
    df = pd.DataFrame(profiles)
    return df.to_csv(index=False).encode('utf-8')

def init_state():
    if "profiles" not in st.session_state:
        st.session_state.profiles = []
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

def make_fake_profiles():
    """Crée 4 faux profils d'exemple (exécuté une seule fois)."""
    fake = [
        {
            "id": "p1",
            "display_name": "Azrael",
            "server": "Croca",
            "roles": ["Mono"],
            "classes": ["Iop"],
            "tags": ["PVM", "Succès"],
            "discord": True,
            "dispo": "Weekends 20:00-23:00",
            "objective": "Full succès dj",
            "bio": "Cherche team pvm chill, dispo soirs.",
        },
        {
            "id": "p2",
            "display_name": "Lilya",
            "server": "Brumaire",
            "roles": ["Duo"],
            "classes": ["Eniripsa", "Sacrieur"],
            "tags": ["PVP"],
            "discord": False,
            "dispo": "Tous les jours après 19:00",
            "objective": "Run songe",
            "bio": "Prefer heal/support, recherche duo stable.",
        },
        {
            "id": "p3",
            "display_name": "Gorim",
            "server": "Oto Mustam",
            "roles": ["Tri"],
            "classes": ["Cra"],
            "tags": ["PVM", "PVP"],
            "discord": True,
            "dispo": "Mercredi soir 21:00",
            "objective": "Farm ressources",
            "bio": "Main DPS, bon esprit, micro actif.",
        },
        {
            "id": "p4",
            "display_name": "Zelvik",
            "server": "Aermine",
            "roles": ["Mono"],
            "classes": ["Sadida"],
            "tags": ["Succes"],
            "discord": True,
            "dispo": "Weekend matin",
            "objective": "Mini-boss succès",
            "bio": "Curieux et patient, aime farm et crafting.",
        },
    ]
    # add small generated avatars
    for p in fake:
        p["avatar_bytes"] = image_to_bytes(make_class_image(",".join(p["classes"])))
    return fake

# ---------------------------
# Init
# ---------------------------
init_state()
if len(st.session_state.profiles) == 0:
    # preload fake profiles (only once)
    st.session_state.profiles.extend(make_fake_profiles())

# ---------------------------
# Sidebar - Filters & Admin
# ---------------------------
st.sidebar.markdown("## 🔎 Filtrer & Rechercher")
servers = ["Tous", "Croca", "Brumaire", "Oto Mustam", "Aermine", "Henual", "Jiva"]
chosen_server = st.sidebar.selectbox("Choisir le serveur", servers)

activity_filters = st.sidebar.multiselect("Activités (filtre)", ["PVM","PVP","Succes"], default=[])
role_filter = st.sidebar.multiselect("Rôle recherché", ["Mono","Duo","Tri"], default=[])
discord_filter = st.sidebar.selectbox("Discord", ["Tous","Avec Discord","Sans Discord"])

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Admin")
if st.sidebar.button("Se connecter en Admin (bypass)"):
    st.session_state.admin = True
    st.sidebar.success("Mode admin activé")
if st.session_state.admin:
    if st.sidebar.button("Se déconnecter Admin"):
        st.session_state.admin = False

# ---------------------------
# Main layout
# ---------------------------
col1, col2 = st.columns([1,2])

with col1:
    st.header("S'inscrire / Créer un profil")
    with st.form("signup", clear_on_submit=False):
        display_name = st.text_input("Pseudo affiché", max_chars=30)
        server = st.selectbox("Serveur", servers[1:])  # skip "Tous"
        # roles: mono/duo/tri (multiselect but store as roles)
        roles = st.multiselect("Je peux jouer en (choisir)", ["Mono","Duo","Tri"], default=["Mono"])
        # classes: allow multiple and limit to common classes
        classes_available = ["Iop","Eniripsa","Sacrieur","Cra","Sadida","Sram","Panda","Feca","Other"]
        classes = st.multiselect("Classes (choisir jusqu'à 3)", classes_available, max_selections=3)
        tags = st.multiselect("Activités", ["PVM","PVP","Succes"], default=["PVM"])
        discord = st.checkbox("Discord disponible ?", value=True)
        # availability: free text for V1; later could be structured
        dispo = st.text_input("Dispos (ex: Weekends 20:00-23:00)", value="Soirs")
        # playtime: average session length
        playtime = st.selectbox("Durée moyenne de session", ["<1h","1-2h","2-4h",">4h"])
        objective = st.selectbox("Objectif temporaire", ["Aucun","Run songe","Full succès dj","Farm ressources"])
        bio = st.text_area("Bio / précisions", max_chars=300)
        upload = st.file_uploader("Photo de profil (optionnel)", type=["png","jpg","jpeg"])
        choose_class_img = st.selectbox("Ou choisir une image de classe", ["Aucune"] + classes_available)
        submitted = st.form_submit_button("Créer mon profil")

        if submitted:
            if not display_name:
                st.warning("Renseigne un pseudo affiché.")
            else:
                new_id = f"user_{len(st.session_state.profiles)+1}_{int(datetime.utcnow().timestamp())}"
                avatar_bytes = None
                if upload is not None:
                    try:
                        img = Image.open(upload).convert("RGB")
                        avatar_bytes = image_to_bytes(img.resize((300,300)))
                    except Exception:
                        st.error("Impossible de lire l'image uploadée.")
                elif choose_class_img != "Aucune":
                    avatar_bytes = image_to_bytes(make_class_image(choose_class_img))
                else:
                    avatar_bytes = image_to_bytes(make_class_image(display_name[:8]))
                profile = {
                    "id": new_id,
                    "display_name": display_name,
                    "server": server,
                    "roles": roles,
                    "classes": classes if classes else ["Other"],
                    "tags": tags,
                    "discord": discord,
                    "dispo": dispo,
                    "playtime": playtime,
                    "objective": objective,
                    "bio": bio,
                    "avatar_bytes": avatar_bytes,
                    "created_at": datetime.utcnow().isoformat(),
                }
                st.session_state.profiles.append(profile)
                st.success("Profil créé ! Tu es ajouté dans la liste publique.")

with col2:
    st.header("Profils disponibles")
    # apply filters
    filtered = st.session_state.profiles
    if chosen_server != "Tous":
        filtered = [p for p in filtered if p.get("server") == chosen_server]
    if activity_filters:
        filtered = [p for p in filtered if any(tag in p.get("tags",[]) for tag in activity_filters)]
    if role_filter:
        filtered = [p for p in filtered if any(r in p.get("roles",[]) for r in role_filter)]
    if discord_filter == "Avec Discord":
        filtered = [p for p in filtered if p.get("discord") is True]
    elif discord_filter == "Sans Discord":
        filtered = [p for p in filtered if p.get("discord") is False]

    st.write(f"Résultats : {len(filtered)} profils")

    # display cards in grid
    cards_per_row = 2
    for i in range(0, len(filtered), cards_per_row):
        cols = st.columns(cards_per_row)
        for j, p in enumerate(filtered[i:i+cards_per_row]):
            with cols[j]:
                st.markdown("---")
                # avatar
                if p.get("avatar_bytes"):
                    st.image(p["avatar_bytes"], width=150)
                st.subheader(p.get("display_name"))
                st.caption(f"{p.get('server')} • {', '.join(p.get('classes',[]))}")
                st.write(f"**Rôle:** {', '.join(p.get('roles',[]))}")
                st.write(f"**Activités:** {', '.join(p.get('tags',[]))}")
                st.write(f"**Discord:** {'Oui' if p.get('discord') else 'Non'}")
                st.write(f"**Dispo:** {p.get('dispo')} • **Session:** {p.get('playtime')}")
                st.write(f"**Objectif:** {p.get('objective')}")
                st.write(p.get("bio",""))
                # small action buttons
                if st.button("Voir profil", key=f"view_{p['id']}"):
                    st.session_state.current_user = p
                    st.experimental_rerun()

# ---------------------------
# Profile viewer modal-like
# ---------------------------
if st.session_state.current_user:
    p = st.session_state.current_user
    st.markdown("---")
    st.header(f"Profil : {p['display_name']}")
    cols = st.columns([1,2])
    with cols[0]:
        if p.get("avatar_bytes"):
            st.image(p["avatar_bytes"], width=240)
        st.write(f"Server: {p.get('server')}")
        st.write(f"Roles: {', '.join(p.get('roles',[]))}")
        st.write(f"Classes: {', '.join(p.get('classes',[]))}")
        st.write(f"Tags: {', '.join(p.get('tags',[]))}")
        st.write(f"Discord: {'Oui' if p.get('discord') else 'Non'}")
    with cols[1]:
        st.write(f"**Bio:** {p.get('bio')}")
        st.write(f"**Disponibilités:** {p.get('dispo')}")
        st.write(f"**Objectif:** {p.get('objective')}")
        if st.button("Fermer profil"):
            st.session_state.current_user = None
            st.experimental_rerun()

# ---------------------------
# Admin panel
# ---------------------------
if st.session_state.admin:
    st.sidebar.markdown("---")
    st.sidebar.header("Admin")
    st.sidebar.write(f"Profils enregistrés: {len(st.session_state.profiles)}")
    if st.sidebar.button("Exporter CSV"):
        csv_bytes = export_profiles_csv(st.session_state.profiles)
        b64 = base64.b64encode(csv_bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="profiles_export.csv">Télécharger profiles_export.csv</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    if st.sidebar.button("Vider profils (reset)"):
        st.session_state.profiles = make_fake_profiles()
        st.sidebar.success("Profils reset !")

    st.sidebar.markdown("### Admin: ajouter profil test rapide")
    if st.sidebar.button("Ajouter profil test"):
        testp = {
            "id": f"test_{int(datetime.utcnow().timestamp())}",
            "display_name": "AdminTest",
            "server": "Croca",
            "roles": ["Mono"],
            "classes": ["Other"],
            "tags": ["PVM"],
            "discord": True,
            "dispo": "Soirs",
            "playtime": "1-2h",
            "objective": "Run songe",
            "bio": "Profil admin ajouté",
            "avatar_bytes": image_to_bytes(make_class_image("Admin")),
            "created_at": datetime.utcnow().isoformat(),
        }
        st.session_state.profiles.append(testp)
        st.sidebar.success("Profil admin ajouté.")

# ---------------------------
# Footer / Notes
# ---------------------------
st.markdown("---")
st.caption("Prototype V1 • Design vert/noir inspiré Dofus/Tinder • Portable → API + mobile app next")
