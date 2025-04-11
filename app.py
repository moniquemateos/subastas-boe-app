import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import tempfile


def scrape_subastas(paginas=2):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

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

            subastas.append({
                "titulo": titulo,
                "detalle": " ".join(detalle),
                "enlace": enlace
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
    st.dataframe(df)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df.to_excel(tmp.name, index=False)
        st.download_button("Descargar Excel", open(tmp.name, "rb"), file_name="subastas_boe.xlsx")
