from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

class Command(BaseCommand):
    help = "Scrapea productos desde Coto Digital usando Selenium"

    def add_arguments(self, parser):
        parser.add_argument("--query", type=str, help="Palabra clave de búsqueda (ej. 'leche')")
        parser.add_argument("--limit", type=int, default=30, help="Cantidad máxima de productos a obtener")
        parser.add_argument("--debug", action="store_true", help="Muestra navegador en modo visible")

    def handle(self, *args, **options):
        query = options["query"] or "leche"
        limit = options["limit"]
        debug = options["debug"]

        print(f"Buscando productos en Coto: {query}")

        chromedriver_autoinstaller.install()

        chrome_options = Options()
        if not debug:
            chrome_options.add_argument("--headless=new")  # headless confiable
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=chrome_options)

        try:
            url = f"https://www.cotodigital.com.ar/sitios/cdigi/browse?Ntt={query}"
            driver.get(url)

            # Scroll para activar carga dinámica
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
                time.sleep(2)

            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3.nombre-producto"))
            )

            productos = driver.find_elements(By.CSS_SELECTOR, "h3.nombre-producto")

            print(f"🔍 Se encontraron {len(productos)} productos (mostrando hasta {limit}):\n")

            for i, producto in enumerate(productos[:limit], start=1):
                nombre = producto.text.strip()
                try:
                    # NUEVO: buscar precio dentro del div.centro-precios del mismo producto
                    precio_elem = producto.find_element(
                        By.XPATH, "./ancestor::div[contains(@class,'centro-precios')]//h4[contains(@class,'card-title')]"
                    )
                    precio = precio_elem.text.strip()
                except:
                    precio = "No encontrado"

                print(f"{i}. {nombre} — {precio}")

            print("\n✅ Scraping finalizado correctamente.")

            if debug:
                input("\nPresioná Enter para cerrar el navegador...")

        except Exception as e:
            print(f"⚠️ Error durante el scraping: {e}")

        finally:
            driver.quit()
