import time
import sys
import numpy as numpy
import pandas as pd
import selenium
from math import floor
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Python script to scrape product data from ALiExpress and Identify trending products bassed on the number of orders and reviews
def scrape_products_by_category(category, num_products):
    chrome_options = Options()
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    try: 
      # Navigate to AliExpress homepage
      driver.get("https://www.aliexpress.com/")
      time.sleep(3)

      # Select USD
      download = driver.find_element_by_xpath('//b[text()="Download the AliExpress app"]')
      download_div = download.find_element(By.XPATH, "..")
      download_parent_container = download_div.find_element(By.XPATH, "..")

      # Currency, Language and country action is the next sibling to download action
      actions_div = download_parent_container.find_element(By.XPATH, "./following-sibling::*")
      actions_div.click()

      time.sleep(2)

      # Select only currency action
      currency_label = driver.find_element_by_xpath('//div[text()="Currency"]')
      currency_dropdown = currency_label.find_element(By.XPATH, "./following-sibling::*") # Currency drawdown is th enext sibling to currency label
      currency_dropdown.click()

      currency_dropdown.find_element_by_xpath('//div[text()="USD ( US Dollar )"]').click() # Select USD
      currency_dropdown.find_element(By.XPATH, "./following-sibling::*").click() # save button

      time.sleep(7)

      # all categories drop down
      all_categories_container = driver.find_element_by_xpath('//div[text()="All Categories"]')
      all_categories_container.click()

      parent_element = all_categories_container.find_element(By.XPATH, "..")
      sibling_element = parent_element.find_element(By.XPATH, "./following-sibling::*")

      categories_ = sibling_element.find_elements(By.TAG_NAME, "a")
      matched_category = None

      for category_item in categories_:
        li_item = category_item.find_element(By.TAG_NAME, "li")
        div_item = li_item.find_element(By.TAG_NAME, "div")

        category_name = div_item.text

        if (category.lower() == category_name.lower()):
          matched_category = category_name
          category_item.click()
          # time.sleep(6)
          break

      if not matched_category:
        raise Exception("Category does not exist on AliExpress")

      SCROLL_PAUSE_TIME = 0.5
      i = 0
      reload_limit = floor(num_products/30)
      last_height = driver.execute_script("return document.body.scrollHeight")

      while i <= reload_limit:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")

        last_height = new_height
        i += 1
      driver.implicitly_wait(10)

      driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
      time.sleep(4)  # wait for all image assets to load

      top_selling = driver.find_element_by_xpath('//div[text()="Top selling"]')

      top_selling_parent = top_selling.find_element(By.XPATH, "..")

      products_parent = top_selling_parent.find_element(By.XPATH, "..")
      parent = products_parent.find_element(By.XPATH, "./following-sibling::*")
      products_container = parent.find_element(By.XPATH, "./div")


      # Find all child div elements directly under the parent element
      products = products_container.find_elements(By.XPATH, "./div")
      products_count = 0

      all_products = []

      while products_count < num_products:
        product_element = products[products_count]
        product_hash = {}

        first_child = product_element.find_element(By.TAG_NAME, "div")

        second_child = first_child.find_element(By.TAG_NAME, "a")

        # find image
        image_div = second_child.find_element(By.XPATH, "./div") # Find the first child div element directly under the parent element
        image_element = second_child.find_element(By.XPATH, "//div//img")

        driver.execute_script("arguments[0].scrollIntoView();", second_child)

        image_link = image_element.get_attribute("src")

        product_hash["image_link"] = image_link

        # Get product name
        product_details = image_div.find_element(By.XPATH, "./following-sibling::*")
        product_title_div = product_details.find_element(By.XPATH, "./div") # Find the first child div element directly under the parent element
        product_title = product_title_div.get_attribute("title")

        product_hash["product_name"] = product_title

        # Get units sold
        products_sold_div = product_title_div.find_element(By.XPATH, "./following-sibling::*")
        products_sold_span = products_sold_div.find_element(By.TAG_NAME, "span")
        products_sold = products_sold_span.text

        product_hash["sold"] = products_sold.split(" ")[0]

        # Get price
        price_div = products_sold_div.find_element(By.XPATH, "./following-sibling::*")
        price_details = price_div.find_elements(By.TAG_NAME, "span")

        price = f"{price_details[1].text}{price_details[2].text}{price_details[3].text}"

        product_hash["currency"] = "USD"
        product_hash["price"] = price 

        all_products.append(product_hash)

        products_count += 1
    finally: 
      driver.quit()

    return all_products

def save_to_csv(products, file_name):
  df = pd.DataFrame(products)
  df.to_csv(file_name)

if __name__ == "__main__":
  # Check if commmand line arguemnts are provided
  if len(sys.argv) != 3:
    print("Usage: python ali_express.py <category> <num_products")
    sys.exit(1)

  print("fetching products....")

  # Get category and number of products from command-line arguments
  category = sys.argv[1]
  num_products = int(sys.argv[2])

  trending_products = scrape_products_by_category(category, num_products)
  save_to_csv(trending_products, "trending_products.csv")

  print("Product fetched and saved successfully")