import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Météo en temps réel",
    page_icon="🌤️",
    layout="wide"
)

def get_connection():
    return psycopg2.connect(
        host="postgres",
        dbname="weather",
        user="user",
        password="pass",
        port=5432
    )

def load_data():
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECT city, timestamp, avg_temp, is_anomaly
            FROM weather_processed
            ORDER BY timestamp DESC
            LIMIT 100
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur de connexion à PostgreSQL : {e}")
        return pd.DataFrame()

# ── TITRE ──────────────────────────────────────────────
st.title("🌤️Votre Météo en Temps Réel")
st.caption("Données collectées via OpenWeatherMap - Rafraîchissement toutes les 10s")

# ── CHARGEMENT ─────────────────────────────────────────
df = load_data()

if df.empty:
    st.warning("Aucune donnée disponible. Vérifiez que le producteur et le processor tournent.")
    time.sleep(10)
    st.rerun()

# ── MÉTRIQUES RÉSUMÉ ───────────────────────────────────
st.subheader("Dernières valeurs")
cols = st.columns(3)
cities = ["Montreal", "Quebec City", "Toronto"]

for i, city in enumerate(cities):
    city_df = df[df["city"] == city]
    if not city_df.empty:
        last = city_df.iloc[0]
        anomaly = "🔴 ANOMALIE" if last["is_anomaly"] else "🟢 Normal"
        cols[i].metric(
            label=city,
            value=f"{last['avg_temp']:.1f} °C",
            delta=anomaly
        )

# ── GRAPHE TEMPÉRATURE ─────────────────────────────────
st.subheader("Évolution de la température moyenne")
df_sorted = df.sort_values("timestamp")

fig = px.line(
    df_sorted,
    x="timestamp",
    y="avg_temp",
    color="city",
    markers=True,
    labels={"avg_temp": "Température moyenne (°C)", "timestamp": "Heure", "city": "Ville"},
    color_discrete_map={
        "Montreal": "#2E75B6",
        "Quebec City": "#2E8B57",
        "Toronto": "#C0392B"
    }
)
fig.update_layout(
    hovermode="x unified",
    legend_title="Ville",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# ── ANOMALIES ──────────────────────────────────────────
anomalies = df[df["is_anomaly"] == True]
st.subheader("Anomalies détectées")
if anomalies.empty:
    st.success("Aucune anomalie détectée pour le moment.")
else:
    st.error(f"⚠️ {len(anomalies)} anomalie(s) détectée(s) !")
    st.dataframe(anomalies, use_container_width=True)

# ── TABLEAU COMPLET ────────────────────────────────────
st.subheader("Historique des 100 dernières mesures")
st.dataframe(
    df.style.apply(
        lambda row: ["background-color: #ffcccc" if row["is_anomaly"] else "" for _ in row],
        axis=1
    ),
    use_container_width=True
)

# ── RAFRAÎCHISSEMENT ───────────────────────────────────
time.sleep(10)
st.rerun()