from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

def scrape_data():
    # Configurar el WebDriver
    driver = webdriver.Chrome()
    driver.get("https://www.compraonline.alcampo.es/categories/bebidas/bebidas-alcoh%C3%B3licas/ron/OC11543?source=navigation")
    
    time.sleep(2)  # Esperar para cargar la página
    
    try:
        # Encontrar las tags de los alcoholes
        alcohols_elements = driver.find_elements(By.CLASS_NAME, "sc-6514kr-0 bZwGZy")
        
        alcohols_data = []
        #De ahi voy a sc-filq44-0 bqTUnq de ahi a footer-container de ahi a _text_16wi0_1 _text--m_16wi0_23 en caso de promos promotion-container y el _text_16wi0_1 _text--m_16wi0_23 sc-1vpsrpe-2 sc-bnzhts-0 jVAYFg kUYwXM que es el precio litro y de aqui sc-mmemlz-0 hbYzCI el price-pack-size-container al sc-mmemlz-0 kImdqr a _text_16wi0_1 _text--m_16wi0_23 sc-1fkdssq-0 bkVLiN
        for alcohol in alcohols_elements:
            alcohol_name = alcohol.find_element(By.CLASS_NAME, "title-container").text
            alcohol_price = alcohol.find_element(By.CLASS_NAME, "price-pack-size-container").text
            alcohols_data.append({"alcohol_name": alcohol_name, "alcohol_price": alcohol_price})
        
        # Guardar los datos en un archivo JSON
        with open("alcoholoc.json", "w", encoding="utf-8") as f:
            json.dump(alcohols_data, f, ensure_ascii=False, indent=4)
        
        print("Scraping exitoso. Datos guardados en alcohols.json")
    
    except Exception as e:
        print(f"Error durante el scraping: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_data()
