import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def url_to_json_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    content = ""
    title = ""

    try:
        # Extract details
        element_present = EC.presence_of_element_located((By.TAG_NAME, 'body'))
        WebDriverWait(driver, 10).until(element_present)
        content = driver.find_element(By.TAG_NAME, 'body').text
        title = driver.find_element(By.TAG_NAME, 'h1').text  # Assuming h1 contains the title
    except Exception as e:
        content = str(e)
    finally:
        driver.quit()

    # Construct the data dictionary
    data = {
        'messages': [{
            'page_content': content,
            'url': url,
            'title': title,
        }]
    }
    
    return data
