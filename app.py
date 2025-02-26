from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def accumulate_products(driver, pause_time=5, max_attempts=5):
    """
    Acumula productos haciendo scroll hasta que no se carguen nuevos productos
    durante 'max_attempts' consecutivos. Además, si se detecta un botón de "Cargar más",
    se simula un clic para forzar la carga de más elementos.
    """
    collected = {}  # Usamos el título como clave para evitar duplicados
    attempts = 0
    last_count = 0

    while attempts < max_attempts:
        # Hacemos scroll hasta el final de la página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        
        # Si existe un botón "Cargar más", se hace clic en él
        try:
            load_more = driver.find_element(By.CSS_SELECTOR, "button.load-more, a.load-more")
            if load_more:
                load_more.click()
                print("Botón 'Cargar más' encontrado y clickeado")
                time.sleep(pause_time)
        except Exception:
            # Si no se encuentra, se continúa con el scroll
            pass
        
        # Buscar los productos actualmente visibles
        products = driver.find_elements(By.CSS_SELECTOR, "div[data-test^='fop-wrapper']")
        print(f"Se encontraron {len(products)} elementos visibles")

        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, "h3[data-test='fop-title']").text.strip()
                if title in collected:
                    continue
                price = product.find_element(By.CSS_SELECTOR, "span[data-test='fop-price']").text.strip()
                try:
                    price_per_liter = product.find_element(By.CSS_SELECTOR, "span[data-test='fop-price-per-unit']").text.strip()
                except:
                    price_per_liter = "No disponible"
                in_promotion = not bool(product.find_elements(By.CSS_SELECTOR, "div.promotion-container"))
                available = bool(product.find_elements(By.CSS_SELECTOR, "div.footer-container"))
                collected[title] = {
                    "nombre": title,
                    "precio": price,
                    "precio_por_litro": price_per_liter,
                    "en_promocion": in_promotion,
                    "disponible": available
                }
                print(f"Producto agregado: {title}")
            except Exception as e:
                print("❌ Error procesando un producto:", e)

        # Comprobar si se han cargado nuevos productos
        if len(collected) == last_count:
            attempts += 1
            print(f"No se detectaron nuevos productos. Intento {attempts} de {max_attempts}.")
        else:
            attempts = 0  # Reiniciamos si se cargaron nuevos productos
            last_count = len(collected)

    return list(collected.values())


def process_link(driver, url, product_type, pause_time=3, max_attempts=3):
    """
    Procesa un link, acumula la información de los productos y la guarda
    en un archivo JSON nombrado según el tipo de producto.
    """
    print(f"Procesando productos de tipo: {product_type}")
    driver.get(url)
    time.sleep(6)  # Espera a que la página cargue completamente
    products_data = accumulate_products(driver, pause_time, max_attempts)
    print(f"🔎 Se han acumulado {len(products_data)} productos para {product_type}.")
    
    # Guardar los datos en un archivo JSON
    filename = f"{product_type}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Datos de {product_type} guardados en {filename}")

def scrape_all_data():
    """
    Inicializa el driver y recorre un array de links para procesarlos según su tipo.
    """
    options = Options()
    options.headless = False  # Cambia a True si prefieres modo headless
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Array de links con su correspondiente tipo de producto
    links = [
        {
            "type": "alcohols",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/bebidas-alcoh%C3%B3licas/OC1154"
        },
        {
            "type": "juices",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/zumos-de-frutas/OC1102?source=navigation"
        },
        {
            "type": "beers",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/cervezas/OC1107?source=navigation"
        },
        {
            "type": "wines_t",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/vino-tinto/OC1151?source=navigation"
        },
        {
            "type": "wines_w",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/vino-blanco/OC1152?source=navigation"
        },
        {
            "type": "champagne",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/champagne-cavas-y-sidras/OC1156?source=navigation"
        },
        {
            "type": "wine_r",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/vino-rosados-frizzantes-dulces-y-olorosos/OC1153?source=navigation"
        },
        {
            "type": "licours",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/licores/OC1155?source=navigation"
        },
        {
            "type": "sodas",
            "url": "https://www.compraonline.alcampo.es/categories/bebidas/refrescos/OC1103?source=navigation"
        },
        {
            "type": "sugars",
            "url": "https://www.compraonline.alcampo.es/categories/desayuno-y-merienda/az%C3%BAcar-miel-y-otros-edulcorantes/OCAzucaryedulcorante?source=navigation"
        }
        # Agrega más links y tipos de productos según sea necesario
    ]

    try:
        for item in links:
            process_link(driver, item["url"], item["type"])
    except Exception as e:
        print(f"⚠️ Error durante el scraping: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_all_data()
