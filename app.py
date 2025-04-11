import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import tempfile

def scrape_subastas(paginas=2):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://subastas.boe.es/subastas_boe_en/CargarInicioSubastasAction.do"
    driver.get(url)
    time.sleep(3)

    buscar_button = driver.find_element(By.ID, "buscar")
    buscar_button.click()
    time.sleep(3)

    subastas = []

    for page in range(1, paginas + 1):
        st.info(f"Extrayendo página {page}")
        rows = driver.find_elements(By.CSS_SELECTOR, ".resultadoSubasta")

        for row in rows:
            enlace = row.find_element(By.TAG_NAME, "a").get_attribute("href")
            titulo = row.find_element(By.TAG_NAME, "a").text
            detalle = row.text.split("\n")

            # Datos simulados para vista previa de tabla enriquecida
            subastas.append({
                "Título": titulo,
                "Tipo de Bien": "Vivienda",
                "Provincia": "Madrid",
                "Deuda Pendiente (€)": 5230.45,
                "Valor Catastral (€)": 120000.00,
                "Valor de Tasación (€)": 115000.00,
                "Importe de Puja Mínima (€)": 57500.00,
                "Fecha de Fin": "20/04/2025",
                "Enlace": enlace
            })

        try:
            siguiente = driver.find_element(By.LINK_TEXT, "Siguiente")
            siguiente.click()
            time.sleep(3)
        except:
            break

    driver.quit()
    return pd.DataFrame(subastas)


st.set_page_config(page_title="Subastas BOE", layout="wide")
st.title("Buscador de Subastas del BOE")
st.markdown("Extrae y explora subastas públicas del portal oficial.")

paginas = st.slider("Nº de páginas a escanear", 1, 10, 2)

if st.button("Extraer subastas"):
    df = scrape_subastas(paginas=paginas)
    st.success(f"{len(df)} subastas extraídas")

    # Filtros interactivos (excluyendo Título y Enlace)
    tipo_bien = st.multiselect("Tipo de Bien", df["Tipo de Bien"].unique())
    provincia = st.multiselect("Provincia", df["Provincia"].unique())

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

    # Aplicar filtros
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
