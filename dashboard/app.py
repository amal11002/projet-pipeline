import os
import time
import pandas as pd
import psycopg2
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Weather Dashboard", layout="wide")

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "weather")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def load_data(limit=300):
    query = f"""
        SELECT
            city,
            temperature,
            humidity,
            wind_speed,
            moving_avg_5min,
            is_anomaly,
            event_time
        FROM weather_processed
        ORDER BY event_time DESC
        LIMIT {limit};
    """

    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        return df
    finally:
        if conn is not None:
            conn.close()

st.title("Dashboard météo en temps réel")
st.caption("Rafraîchissement automatique toutes les 10 secondes")

try:
    df = load_data()

    if df.empty:
        st.warning("Aucune donnée trouvée dans weather_processed.")
    else:
        df["event_time"] = pd.to_datetime(df["event_time"])
        df = df.sort_values("event_time")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Courbe de température en temps réel")
            fig = px.line(
                df,
                x="event_time",
                y="temperature",
                color="city",
                markers=True,
                title="Évolution de la température"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("État des anomalies")
            anomalies = df[df["is_anomaly"] == True]

            if not anomalies.empty:
                last_anomaly = anomalies.iloc[-1]
                st.error(
                    f"Anomalie détectée à {last_anomaly['city']} | "
                    f"{last_anomaly['temperature']} °C"
                )
            else:
                st.success("Aucune anomalie détectée")

            latest = df.iloc[-1]
            st.metric("Dernière température", f"{latest['temperature']} °C")
            st.metric("Dernière moyenne glissante", f"{latest['moving_avg_5min']} °C")
            st.metric("Dernière ville", f"{latest['city']}")

        st.subheader("Dernières valeurs")
        st.dataframe(
            df.sort_values("event_time", ascending=False).head(20),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")

time.sleep(10)
st.rerun()