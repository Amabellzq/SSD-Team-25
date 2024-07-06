import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def test_shop_page(driver):
    # Open the shop page
    driver.get(' https://shoppp.me/shop')

    # Verify the title
    assert "Shop Page - ShopMe" in driver.title

    # Verify the breadcrumb links
    home_breadcrumb = driver.find_element(By.XPATH, "//a[@href='/' and contains(., 'Home')]")
    shop_breadcrumb = driver.find_element(By.XPATH, "//a[@href='/shop' and contains(., 'Shop')]")
    assert home_breadcrumb is not None
    assert shop_breadcrumb is not None

    # Verify the sidebar categories
    categories_section_title = driver.find_element(By.XPATH, "//div[@class='section-title']/h4[text()='Categories']")
    assert categories_section_title is not None

    # Verify categories links
    categories = driver.find_elements(By.XPATH, "//div[@class='categories__accordion']//a")
    for category in categories:
        assert category.get_attribute('href') is not None

    # Verify products in the gallery
    products = driver.find_elements(By.XPATH, "//div[@class='product__item']")
    assert len(products) > 0  # Ensure there is at least one product

    # Verify pagination
    pagination = driver.find_element(By.XPATH, "//div[@class='pagination__option']")
    assert pagination is not None

    # Optional: Print the product names and prices for debugging
    for product in products:
        product_name = product.find_element(By.XPATH, ".//h6/a").text
        product_price = product.find_element(By.XPATH, ".//div[@class='product__price']").text
        print(f"Product: {product_name}, Price: {product_price}")

    # Wait for a while to see the browser in action (optional)
    time.sleep(3)

