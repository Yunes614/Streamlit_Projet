import streamlit as st
import paho.mqtt.client as mqtt
import time

st.set_page_config(page_title="Projet : Serre Intelligente", layout="wide")

# ---------------- VARIABLES MQTT ----------------
mqtt_values = {"connected": False, "temp": "—", "hum": "—", "ldr": "—"}

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    mqtt_values["connected"] = True
    client.subscribe("esp32/temp")
    client.subscribe("esp32/hum")
    client.subscribe("esp32/LDR")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if msg.topic == "esp32/temp":
        mqtt_values["temp"] = payload
    elif msg.topic == "esp32/hum":
        mqtt_values["hum"] = payload
    elif msg.topic == "esp32/LDR":
        mqtt_values["ldr"] = payload

# ---------------- MQTT CLIENT ----------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("20.203.237.89", 1883, 60)
client.loop_start()

# ---------------- CSS DESIGN DE LA DEUXIÈME DASHBOARD ----------------
st.markdown("""
<style>

.title {
    text-align:center;
    font-size:68px;
    font-weight:900;
    color:#2b303b;
}

.subtitle {
    text-align:center;
    font-size:30px;
    color:#6b7280;
    margin-top:-15px;
    margin-bottom:30px;
}

.status {
    background:#f3fce3;
    padding:18px;
    border-radius:12px;
    font-size:22px;
    color:#2c3e1f;
    text-align:center;
    margin-bottom:25px;
}

.card {
    background:white;
    padding:40px 25px;
    border-radius:25px;
    box-shadow:0 5px 25px rgba(0,0,0,0.07);
    text-align:center;
    margin:15px;
}

.label {
    font-size:24px;
    color:#374151;
    font-weight:600;
}

.value {
    font-size:50px;
    font-weight:800;
    margin-top:15px;
    color:#111827;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITRE ----------------
st.markdown("<div class='title'>🌿 Projet : Serre Intelligente</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Dashboard IoT – ESP32</div>", unsafe_allow_html=True)

# ---------------- BOUCLE TEMPS RÉEL (TON CODE QUI FONCTIONNE) ----------------
placeholder = st.empty()

while True:
    with placeholder.container():

        # -------- STATUT MQTT --------
        if mqtt_values["connected"]:
            st.markdown("<div class='status'>✔ Connecté au broker MQTT</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status'>⏳ Connexion en attente…</div>", unsafe_allow_html=True)

        # -------- AFFICHAGE DES DONNÉES --------
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
            <div class='card'>
                <div class='label'>🌡 Température</div>
                <div class='value'>{mqtt_values['temp']}</div>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <div class='card'>
                <div class='label'>💧 Humidité</div>
                <div class='value'>{mqtt_values['hum']}</div>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <div class='card'>
                <div class='label'>🔆 Luminosité LDR</div>
                <div class='value'>{mqtt_values['ldr']}</div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1)
