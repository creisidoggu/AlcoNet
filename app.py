from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def accumulate_products(driver, pause_time=2, max_attempts=20):
    """
    Acumula los productos mientras se hace scroll en la ventana.
    Debido a la virtualización, el DOM solo muestra una parte de los productos a la vez,
    por lo que se recogen los datos de los elementos visibles en cada iteración.
    """
    collected = {}  # Usamos el título como clave para evitar duplicados
    attempts = 0
    last_total = 0

    while attempts < max_attempts:
        try:
            parent = driver.find_element(By.CSS_SELECTOR, "div[data-retailer-anchor='product-list']")
            products = parent.find_elements(By.CSS_SELECTOR, "div[data-test^='fop-wrapper']")
        except Exception as e:
            print("❌ Error al localizar el contenedor de productos:", e)
            products = []

        # Recorrer los productos visibles y acumular su información
        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, "h3[data-test='fop-title']").text.strip()
                if title in collected:
                    continue  # Ya fue procesado
                price = product.find_element(By.CSS_SELECTOR, "span[data-test='fop-price']").text.strip()
                try:
                    price_per_liter = product.find_element(By.CSS_SELECTOR, "span[data-test='fop-price-per-unit']").text.strip()
                except:
                    price_per_liter = "No disponible"
                in_promotion = bool(product.find_elements(By.CSS_SELECTOR, "div.promotion-container"))
                available = bool(product.find_elements(By.CSS_SELECTOR, "div.footer-container"))
                collected[title] = {
                    "nombre": title,
                    "precio": price,
                    "precio_por_litro": price_per_liter,
                    "en_promocion": in_promotion,
                    "disponible": available
                }
                print(f"✅ Producto agregado: {title}")
            except Exception as e:
                print("❌ Error procesando un producto:", e)
        
        current_total = len(collected)
        print(f"Total acumulado hasta ahora: {current_total}")
        
        if current_total == last_total:
            attempts += 1
        else:
            attempts = 0
            last_total = current_total

        # Realiza un pequeño scroll en la ventana para cargar nuevos productos
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(pause_time)
    
    print(f"✅ Acumulación finalizada. Total productos acumulados: {len(collected)}")
    return list(collected.values())

def process_link(driver, url, product_type):
    """
    Carga la URL, acumula los productos (mientras se hace scroll) y guarda los datos en un JSON.
    """
    print(f"📡 Procesando productos de tipo: {product_type}")
    driver.get(url)
    time.sleep(6)  # Espera inicial para que la página cargue completamente

    products_data = accumulate_products(driver, pause_time=2, max_attempts=20)
    print(f"📊 Se han acumulado {len(products_data)} productos para {product_type}.")
    
    # Guardar los datos en un archivo JSON
    filename = f"{product_type}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Datos de {product_type} guardados en {filename}")

def scrape_all_data():
    """
    Inicializa el driver y procesa la(s) categoría(s) especificada(s).
    """
    options = Options()
    options.headless = False  # Cambia a True para modo headless
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Procesamos la categoría (en este ejemplo, alcoholes)
    links = [
        {"type": "alcohols", "url": "https://www.compraonline.alcampo.es/categories/bebidas/bebidas-alcoh%C3%B3licas/OC1154"},
        {"type": "sodas", "url": "https://www.compraonline.alcampo.es/categories/bebidas/refrescos/OC1103"},
    ]
    
    try:
        for item in links:
            process_link(driver, item["url"], item["type"])
    except Exception as e:
        print(f"⚠️ Error durante el scraping: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Inicia el temporizador
    start_time = time.time()

    scrape_all_data()

    # Calcula y muestra el tiempo de ejecución
    elapsed_time = time.time() - start_time
    print(f"⏱ El programa terminó en {elapsed_time:.2f} segundos.")
