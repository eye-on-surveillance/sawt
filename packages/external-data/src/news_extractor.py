import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def url_to_json_selenium(url, retries=3, retry_delay=10):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    for _ in range(retries):
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(120)

        try:
            driver.get(url)

            element_present = EC.presence_of_element_located((By.TAG_NAME, "body"))
            WebDriverWait(driver, 20).until(element_present)
            content = driver.find_element(By.TAG_NAME, "body").text
            title = driver.find_element(By.TAG_NAME, "h1").text
            driver.quit()

            data = {
                "messages": [
                    {
                        "page_content": content,
                        "url": url,
                        "title": title,
                    }
                ]
            }
            return data

        except Exception as e:
            driver.quit()
            if _ < retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"Exception for URL {url}: {e}")
                return None
