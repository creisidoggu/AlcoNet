from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def accumulate_products(driver, pause_time=3, step=300, max_scrolls=50):
    collected = {}  # Usamos el título como clave para evitar duplicados
    current_position = 0
    scrolls = 0
    document_height = driver.execute_script("return document.body.scrollHeight")
    
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, arguments[0]);", current_position)
        time.sleep(pause_time)
        
        # Buscar los productos actualmente visibles
        products = driver.find_elements(By.CSS_SELECTOR, "div[data-test^='fop-wrapper']")
        print(f"Scroll {scrolls+1}: se encontraron {len(products)} elementos visibles")
        
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
                in_promotion = bool(product.find_elements(By.CSS_SELECTOR, "div.promotion-container"))
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
        
        scrolls += 1
        current_position += step
        # Actualizar la altura del documento en caso de que haya aumentado
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > document_height:
            document_height = new_height
        if current_position > document_height:
            break

    return list(collected.values())

def scrape_data():
    options = Options()
    options.headless = False  # Cambia a True si prefieres no ver el navegador
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.compraonline.alcampo.es/categories/bebidas/bebidas-alcoh%C3%B3licas/ron/OC11543?source=navigation")
    
    try:
        # Esperar un poco al cargar la página inicialmente
        time.sleep(5)
        
        # Acumular productos haciendo scroll incremental
        alcohols_data = accumulate_products(driver, pause_time=3, step=300, max_scrolls=50)
        print(f"🔎 Se han acumulado {len(alcohols_data)} productos.")
        
        # Guardar los datos en un archivo JSON
        with open("alcohols.json", "w", encoding="utf-8") as f:
            json.dump(alcohols_data, f, ensure_ascii=False, indent=4)
        
        print("✅ Scraping exitoso. Datos guardados en alcohols.json")
    
    except Exception as e:
        print(f"⚠️ Error durante el scraping: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_data()
