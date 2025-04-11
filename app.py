import streamlit as st
import pandas as pd
import tempfile

st.set_page_config(page_title="Subastas BOE 🌟", layout="wide")
st.title("🗂️ Buscador de Subastas del BOE")
st.markdown("Bienvenido a tu herramienta profesional de análisis de subastas públicas. Carga un archivo CSV para empezar a explorar oportunidades 🏠🚗🏢")

archivo = st.file_uploader("📤 Sube un archivo CSV con subastas extraídas", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)

    st.success(f"✅ {len(df)} subastas cargadas correctamente")

    with st.expander("🔎 Filtrar subastas", expanded=True):
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            tipo_bien = st.multiselect("🏷️ Tipo de Bien", df["Tipo de Bien"].dropna().unique())
        with col2:
            provincia = st.multiselect("📍 Provincia", df["Provincia"].dropna().unique())

        col4, col5 = st.columns(2)
        with col4:
            deuda_min, deuda_max = st.slider("💸 Deuda Pendiente (€)",
                                             float(df["Deuda Pendiente (€)"].min()),
                                             float(df["Deuda Pendiente (€)"].max()),
                                             (float(df["Deuda Pendiente (€)"].min()), float(df["Deuda Pendiente (€)"].max())))

            valor_cat_min, valor_cat_max = st.slider("🏠 Valor Catastral (€)",
                                                     float(df["Valor Catastral (€)"].min()),
                                                     float(df["Valor Catastral (€)"].max()),
                                                     (float(df["Valor Catastral (€)"].min()), float(df["Valor Catastral (€)"].max())))

        with col5:
            tasacion_min, tasacion_max = st.slider("📏 Valor de Tasación (€)",
                                                   float(df["Valor de Tasación (€)"].min()),
                                                   float(df["Valor de Tasación (€)"].max()),
                                                   (float(df["Valor de Tasación (€)"].min()), float(df["Valor de Tasación (€)"].max())))

            puja_min, puja_max = st.slider("🔨 Importe de Puja Mínima (€)",
                                           float(df["Importe de Puja Mínima (€)"].min()),
                                           float(df["Importe de Puja Mínima (€)"].max()),
                                           (float(df["Importe de Puja Mínima (€)"].min()), float(df["Importe de Puja Mínima (€)"].max())))

    df_filtrado = df.copy()
    if tipo_bien:
        df_filtrado = df_filtrado[df_filtrado["Tipo de Bien"].isin(tipo_bien)]
    if provincia:
        df_filtrado = df_filtrado[df_filtrado["Provincia"].isin(provincia)]

    df_filtrado = df_filtrado[
        (df_filtrado["Deuda Pendiente (€)"] >= deuda_min) & (df_filtrado["Deuda Pendiente (€)"] <= deuda_max) &
        (df_filtrado["Valor Catastral (€)"] >= valor_cat_min) & (df_filtrado["Valor Catastral (€)"] <= valor_cat_max) &
        (df_filtrado["Valor de Tasación (€)"] >= tasacion_min) & (df_filtrado["Valor de Tasación (€)"] <= tasacion_max) &
        (df_filtrado["Importe de Puja Mínima (€)"] >= puja_min) & (df_filtrado["Importe de Puja Mínima (€)"] <= puja_max)
    ]

    st.markdown("### 📋 Resultados filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df_filtrado.to_excel(tmp.name, index=False)
        st.download_button("⬇️ Descargar Excel", open(tmp.name, "rb"), file_name="subastas_boe_filtradas.xlsx")
else:
    st.warning("⚠️ Por favor, sube un archivo CSV con los datos de subastas para comenzar.")
