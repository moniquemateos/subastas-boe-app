import streamlit as st
import pandas as pd
import tempfile

st.set_page_config(page_title="Subastas BOE (modo seguro)", layout="wide")
st.title("Buscador de Subastas del BOE (datos cargados)")
st.markdown("Esta app muestra subastas preextraídas del BOE. Los datos pueden actualizarse cargando un nuevo archivo CSV.")

# Cargar CSV local (simulado o generado por scraping externo)
archivo = st.file_uploader("Sube un archivo CSV con subastas extraídas", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)

    st.success(f"{len(df)} subastas cargadas")

    # Filtros interactivos
    tipo_bien = st.multiselect("Tipo de Bien", df["Tipo de Bien"].dropna().unique())
    provincia = st.multiselect("Provincia", df["Provincia"].dropna().unique())

    deuda_min, deuda_max = st.slider("Rango de Deuda Pendiente (€)",
                                     float(df["Deuda Pendiente (€)"].min()),
                                     float(df["Deuda Pendiente (€)"].max()),
                                     (float(df["Deuda Pendiente (€)"].min()), float(df["Deuda Pendiente (€)"].max())))

    valor_cat_min, valor_cat_max = st.slider("Valor Catastral (€)",
                                             float(df["Valor Catastral (€)"].min()),
                                             float(df["Valor Catastral (€)"].max()),
                                             (float(df["Valor Catastral (€)"].min()), float(df["Valor Catastral (€)"].max())))

    tasacion_min, tasacion_max = st.slider("Valor de Tasación (€)",
                                           float(df["Valor de Tasación (€)"].min()),
                                           float(df["Valor de Tasación (€)"].max()),
                                           (float(df["Valor de Tasación (€)"].min()), float(df["Valor de Tasación (€)"].max())))

    puja_min, puja_max = st.slider("Importe de Puja Mínima (€)",
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

    st.dataframe(df_filtrado)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df_filtrado.to_excel(tmp.name, index=False)
        st.download_button("Descargar Excel", open(tmp.name, "rb"), file_name="subastas_boe_filtradas.xlsx")
else:
    st.warning("Por favor, sube un archivo CSV con los datos de subastas para comenzar.")
