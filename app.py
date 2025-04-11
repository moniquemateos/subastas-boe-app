import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import tempfile

def extraer_detalle(driver, enlace):
    driver.get(enlace)
    time.sleep(2)

    def extraer_texto(xpath):
        try:
            return driver.find_element(By.XPATH, xpath).text.strip().replace(".", "").replace(",", ".")
        except:
            return ""

    return {
        "Tipo de Bien": extraer_texto("//td[contains(text(),'Tipo de bien')]/following-sibling::td"),
        "Provincia": extraer_texto("//td[contains(text(),'Provincia')]/following-sibling::td"),
        "Deuda Pendiente (€)": float(extraer_texto("//td[contains(text(),'Deuda pendiente')]/following-sibling::td") or 0),
        "Valor Catastral (€)": float(extraer_texto("//td[contains(text(),'Valor catastral')]/following-sibling::td") or 0),
        "Valor de Tasación (€)": float(extraer_texto("//td[contains(text(),'Valor de tasación')]/following-sibling::td") or 0),
        "Importe de Puja Mínima (€)": float(extraer_texto("//td[contains(text(),'Importe mínimo')]/following-sibling::td") or 0),
        "Fecha de Fin": extraer_texto("//td[contains(text(),'Fin de la subasta')]/following-sibling::td")
    }

def scrape_subastas(paginas=2, limite_por_pagina=5):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://subastas.boe.es/subastas_boe_en/CargarInicioSubastasAction.do"
    driver.get(url)
    time.sleep(3)

    driver.find_element(By.ID, "buscar").click()
    time.sleep(3)

    subastas = []

    for page in range(1, paginas + 1):
        st.info(f"Extrayendo página {page}")
        rows = driver.find_elements(By.CSS_SELECTOR, ".resultadoSubasta")[:limite_por_pagina]

        for row in rows:
            enlace = row.find_element(By.TAG_NAME, "a").get_attribute("href")
            titulo = row.find_element(By.TAG_NAME, "a").text

            detalle = extraer_detalle(driver, enlace)
            detalle.update({"Título": titulo, "Enlace": enlace})
            subastas.append(detalle)

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

paginas = st.slider("Nº de páginas a escanear", 1, 5, 1)
limite = st.slider("Subastas por página", 1, 10, 3)

if st.button("Extraer subastas"):
    df = scrape_subastas(paginas=paginas, limite_por_pagina=limite)
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
