import streamlit as st
import paho.mqtt.client as mqtt
import time
import pandas as pd

st.set_page_config(page_title="Serre Intelligente", layout="wide")

# ---------------- VARIABLES ----------------
if "motor_toggle" not in st.session_state:
    st.session_state.motor_toggle = False

if "motor_speed" not in st.session_state:
    st.session_state.motor_speed = 0

mqtt_values = {"connected": False, "temp": None, "hum": None, "ldr": None}
history = []

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    mqtt_values["connected"] = True
    client.subscribe("esp32/temp")
    client.subscribe("esp32/hum")
    client.subscribe("esp32/LDR")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    if msg.topic == "esp32/temp":
        mqtt_values["temp"] = float(payload)
    elif msg.topic == "esp32/hum":
        mqtt_values["hum"] = float(payload)
    elif msg.topic == "esp32/LDR":
        mqtt_values["ldr"] = float(payload)

# ---------------- MQTT CLIENT ----------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("20.203.237.89", 1883, 60)
client.loop_start()

# ---------------- CSS ----------------
st.markdown("""
<style>
.title { text-align:center; font-size:60px; font-weight:900; }
.subtitle { text-align:center; font-size:24px; margin-bottom:20px; }
.card {
    background:white; padding:30px; border-radius:20px;
    box-shadow:0 4px 20px rgba(0,0,0,0.1); text-align:center;
}
.value { font-size:45px; font-weight:900; }

div[data-testid="stWidgetCheckbox"] {
    transform: scale(1.6);
    margin-top: 20px;
}
div[data-testid="stWidgetLabel"] p {
    font-size: 22px !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITRES ----------------
st.markdown("<div class='title'>🌿 Serre Intelligente</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Dashboard IoT – ESP32</div>", unsafe_allow_html=True)


# ---------------- INTERFACE ----------------
placeholder = st.empty()

while True:
    with placeholder.container():

        # -----------------------------------
        # STATUT BROKER
        # -----------------------------------
        if mqtt_values["connected"]:
            st.success("✔ Connecté au broker MQTT")
        else:
            st.warning("⏳ Connexion...")

        # -----------------------------------
        # CARTES AFFICHAGE
        # -----------------------------------
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='card'><h3>🌡 Température</h3><div class='value'>{mqtt_values['temp']}</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h3>💧 Humidité</h3><div class='value'>{mqtt_values['hum']}</div></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h3>🔆 LDR</h3><div class='value'>{mqtt_values['ldr']}</div></div>", unsafe_allow_html=True)

        # -----------------------------------
        # HISTORIQUE
        # -----------------------------------
        if mqtt_values["temp"] is not None:
            history.append({
                "time": time.strftime("%H:%M:%S"),
                "temp": mqtt_values["temp"],
                "hum": mqtt_values["hum"],
                "ldr": mqtt_values["ldr"]
            })
            history[:] = history[-50:]

        df = pd.DataFrame(history)

        st.subheader("📈 Évolution des mesures")

        if len(df) > 1:
            g1, g2, g3, g4 = st.columns(4)

            with g1:
                st.markdown("### 🌡 Température (°C)")
                st.line_chart(df.set_index("time")[["temp"]])

            with g2:
                st.markdown("### 💧 Humidité (%)")
                st.line_chart(df.set_index("time")[["hum"]])

            with g3:
                st.markdown("### 🔆 Luminosité LDR")
                st.line_chart(df.set_index("time")[["ldr"]])

            # -----------------------------------
            # CONTROLE MOTEUR (ZERO ERREUR)
            # -----------------------------------
            with g4:
                st.markdown("### ⚙️ Moteur")

                st.session_state.motor_toggle = st.toggle(
                    "Activer le moteur",
                    value=st.session_state.motor_toggle,
                    key="motor_toggle_FINAL"
                )

                st.session_state.motor_speed = st.slider(
                    "Vitesse du moteur",
                    50, 100,
                    st.session_state.motor_speed,
                    key="motor_speed_FINAL"
                )

                client.publish("esp32/moteur", "true" if st.session_state.motor_toggle else "false")
                client.publish("esp32/speed", st.session_state.motor_speed)

    time.sleep(1)
