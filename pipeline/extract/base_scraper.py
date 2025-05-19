from abc import ABC, abstractmethod
from util.browser import get_browser
from util.logger import logger

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.browser = None
        self.playwright = None

    def setup(self):
        self.browser, self.playwright = get_browser()

    def teardown(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def extract(self):
        logger.info(f"Iniciando extração de: {self.__class__.__name__}")
        self.setup()
        all_ads = []
        try:
            page = self.browser.new_page()
            logger.debug(f"Acessando URL: {self.base_url}")
            page.goto(self.base_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            ads = self.get_ads(page)
            logger.info(f"{len(ads)} anúncios encontrados.")
            for index, ad in enumerate(ads):
                try:
                    ad_data = self.parse_ad(ad, page)
                    if ad_data:
                        all_ads.extend(ad_data) if isinstance(ad_data, list) else all_ads.append(ad_data)
                except Exception as e:
                    logger.warning(f"[{index}] Falha ao extrair anúncio: {e}")
        except Exception as e:
            logger.error(f"Erro durante a extração: {e}")
        finally:
            self.teardown()
            logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")
        return all_ads

    @abstractmethod
    def get_ads(self, page):
        pass

    @abstractmethod
    def parse_ad(self, ad, page):
        pass