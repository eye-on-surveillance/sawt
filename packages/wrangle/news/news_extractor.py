import re
import spacy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

nlp = spacy.load("en_core_web_sm")


def sanitize_filename(title):
    title_with_spaces = title.replace("_", " ")

    doc = nlp(title_with_spaces)
    tokens = []

    for i, token in enumerate(doc):
        # If it's an acronym (full uppercase):
        if token.text.isupper():
            tokens.append(token.text)
        # If it's the first word of the title or follows a punctuation:
        elif i == 0 or doc[i - 1].text in [".", ";", ":", "?", "!"]:
            tokens.append(token.text.capitalize())
        # For all other words:
        else:
            tokens.append(token.text.lower())

    capitalized_title = " ".join(tokens)

    sanitized = re.sub(r"[^\w\s-]", "", capitalized_title)
    sanitized = " ".join(sanitized.split())

    max_len = 200
    return sanitized[:max_len]


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
            raw_title = driver.find_element(By.TAG_NAME, "h1").text
            sanitized_title = sanitize_filename(raw_title)
            driver.quit()

            data = {
                "messages": [
                    {
                        "page_content": content,
                        "url": url,
                        "title": sanitized_title,
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
