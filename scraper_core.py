import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DarazScraper:
    def __init__(self, use_selenium=True):
        self.base_url = "https://www.daraz.com.np"
        self.use_selenium = use_selenium
        self.driver = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.use_selenium:
            self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options for web scraping"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            print("Selenium driver initialized successfully")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Falling back to requests method...")
            self.use_selenium = False
    
    def close_driver(self):
        """Close the Selenium driver"""
        if self.driver:
            self.driver.quit()
        
    def get_full_url(self, path):
        """Convert relative URL to absolute URL"""
        if not path or path.startswith('http'):
            return path
        return urljoin(self.base_url, path)

    def scrape_with_selenium(self, url):
        """Scrape using Selenium for dynamic content"""
        try:
            print(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-qa-locator="product-item"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.gridItem--Yd0sa')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-tracking="product-card"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.search-card-item'))
                    )
                )
                print("Products loaded successfully")
            except TimeoutException:
                print("Timeout waiting for products, trying with current content...")
            
            # Scroll to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            html = self.driver.page_source
            return BeautifulSoup(html, 'html.parser')
            
        except Exception as e:
            print(f"Error with Selenium scraping: {e}")
            if self.driver:
                return BeautifulSoup(self.driver.page_source, 'html.parser')
            return None

    def scrape_with_requests(self, url):
        """Fallback method using requests"""
        try:
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error with requests: {e}")
            return None

    def extract_product_data(self, product_element):
        """Extract product data from a product element"""
        try:
            # Multiple selectors for different page layouts
            title_selectors = [
                '.title--wFj93 a',
                '.title a', 
                '[data-qa-locator="product-item"] .c16H9d a',
                '.c16H9d a',
                'a[title]',
                'h3 a'
            ]
            
            price_selectors = [
                '.price--NVB62',
                '.price span',
                '.c13VH6',
                '.current-price',
                '[data-qa-locator="product-price"]'
            ]
            
            original_price_selectors = [
                '.origPrice--AoCxF',
                '.original-price',
                '.c1hkC1'
            ]
            
            rating_selectors = [
                '.rating--ZI3Ol',
                '.rating',
                '.c6LcCO'
            ]
            
            reviews_selectors = [
                '.rate--DCc0D',
                '.rate',
                '.c6LcCO + span'
            ]
            
            image_selectors = [
                '.image--WOyuZ img',
                '.image img',
                'img[data-qa-locator="product-image"]',
                'img'
            ]
            
            # Extract title and URL
            title_elem = None
            product_url = ""
            for selector in title_selectors:
                title_elem = product_element.select_one(selector)
                if title_elem:
                    break
            
            if title_elem:
                relative_url = title_elem.get('href', '')
                product_url = self.get_full_url(relative_url)
            
            # Extract price
            price_elem = None
            for selector in price_selectors:
                price_elem = product_element.select_one(selector)
                if price_elem:
                    break
            
            # Extract original price
            original_price_elem = None
            for selector in original_price_selectors:
                original_price_elem = product_element.select_one(selector)
                if original_price_elem:
                    break
            
            # Extract rating
            rating_elem = None
            for selector in rating_selectors:
                rating_elem = product_element.select_one(selector)
                if rating_elem:
                    break
            
            # Extract reviews count
            reviews_elem = None
            for selector in reviews_selectors:
                reviews_elem = product_element.select_one(selector)
                if reviews_elem:
                    break
            
            # Extract image
            image_elem = None
            for selector in image_selectors:
                image_elem = product_element.select_one(selector)
                if image_elem and image_elem.get('src'):
                    break
            
            # Calculate discount if both prices available
            discount = None
            if price_elem and original_price_elem:
                try:
                    current_price = float(re.sub(r'[^\d.]', '', price_elem.get_text().replace(',', '')))
                    orig_price = float(re.sub(r'[^\d.]', '', original_price_elem.get_text().replace(',', '')))
                    if orig_price > current_price:
                        discount = f"{int(((orig_price - current_price) / orig_price) * 100)}% off"
                except:
                    pass
            
            return {
                'title': title_elem.get_text(strip=True) if title_elem else "N/A",
                'price': price_elem.get_text(strip=True) if price_elem else "N/A",
                'original_price': original_price_elem.get_text(strip=True) if original_price_elem else None,
                'discount': discount,
                'rating': rating_elem.get('aria-label', rating_elem.get_text(strip=True)) if rating_elem else "No rating",
                'reviews': reviews_elem.get_text(strip=True) if reviews_elem else "0",
                'image_url': self.get_full_url(image_elem.get('src', '')) if image_elem else "N/A",
                'product_url': product_url
            }
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None

    def scrape_category(self, category, start_page=1, end_page=1):
        """Scrape products from a category"""
        all_products = []
        
        for page in range(start_page, end_page + 1):
            url = f"{self.base_url}/{category}/?page={page}"
            print(f"Scraping page {page}: {url}")
            
            try:
                # Choose scraping method
                if self.use_selenium and self.driver:
                    soup = self.scrape_with_selenium(url)
                else:
                    soup = self.scrape_with_requests(url)
                
                if not soup:
                    print(f"Failed to get content from page {page}")
                    continue
                
                # Multiple selectors for product containers
                product_selectors = [
                    '[data-qa-locator="product-item"]',
                    '.gridItem--Yd0sa',
                    '[data-tracking="product-card"]',
                    '.search-card-item',
                    '.c2prKC'
                ]
                
                products = []
                for selector in product_selectors:
                    products = soup.select(selector)
                    if products:
                        print(f"Found {len(products)} products using selector: {selector}")
                        break
                
                if not products:
                    print(f"No products found on page {page}")
                    print("Available classes:", [elem.get('class') for elem in soup.find_all()[:10] if elem.get('class')])
                    continue
                
                page_products = 0
                for product in products:
                    product_data = self.extract_product_data(product)
                    if product_data and product_data['title'] != "N/A":
                        product_data.update({
                            'category': category,
                            'page': page
                        })
                        all_products.append(product_data)
                        page_products += 1
                
                print(f"Successfully extracted {page_products} products from page {page}")
                
                # Add delay between pages
                if page < end_page:
                    time.sleep(random.uniform(3, 6))
                    
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
        
        return all_products 