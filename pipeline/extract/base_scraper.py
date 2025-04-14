from playwright.sync_api import sync_playwright
import time

class BaseScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.page = None

    def start_browser(self):
        """Inicia o navegador (Chromium por padrão)"""
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            return self.page

    def close_browser(self):
        """Fecha o navegador"""
        if self.browser:
            self.browser.close()

    def navigate_to(self, url):
        """Navega até o URL especificado"""
        if self.page:
            self.page.goto(url)

    def get_page_title(self):
        """Retorna o título da página atual"""
        if self.page:
            return self.page.title()

    def wait_for_selector(self, selector, timeout=5000):
        """Aguarda um elemento aparecer na página"""
        if self.page:
            self.page.wait_for_selector(selector, timeout=timeout)

    def extract_data(self, selector):
        """Extrai texto do elemento especificado"""
        if self.page:
            element = self.page.query_selector(selector)
            return element.inner_text() if element else None

    def scroll_page(self):
        """Rola a página para baixo (pode ser útil para carregar conteúdo dinâmico)"""
        if self.page:
            self.page.mouse.wheel(0, 1000)
            time.sleep(2)

    def scrape(self, url):
        """Método principal para rodar o scraping"""
        try:
            self.start_browser()
            self.navigate_to(url)
            
            print(f"Page Title: {self.get_page_title()}")

            data = self.extract_data('.nome-da-classe')
            print(f"Extracted Data: {data}")

            self.scroll_page()
        
        finally:
            self.close_browser()
