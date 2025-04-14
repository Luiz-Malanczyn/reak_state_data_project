from playwright.sync_api import sync_playwright
import time
from urllib.parse import urlencode, urljoin

class BaseScraper:
    def __init__(self, headless=True, filters=None):
        """
        Inicializa a classe com o navegador e os filtros.

        :param headless: Se o navegador será iniciado no modo headless (sem interface gráfica).
        :param filters: Um dicionário com os filtros a serem aplicados na pesquisa.
        """
        self.headless = headless
        self.filters = filters if filters else {}
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

    def build_search_url(self, base_url):
        """
        Constrói a URL de pesquisa com base nos filtros fornecidos.

        :param base_url: A URL base para a pesquisa.
        :return: A URL final com os filtros aplicados.
        """
        if not self.filters:
            return base_url

        query_params = {key: value for key, value in self.filters.items() if value is not None}
        
        if '?' in base_url:
            return f"{base_url}&{urlencode(query_params)}"
        else:
            return f"{base_url}?{urlencode(query_params)}"

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