from abc import ABC, abstractmethod
from util.browser import get_browser
from util.browser import launch_browser
from util.logger import logger

class BaseScraper(ABC):
    def __init__(self, base_url: str, playwright):
        self.base_url = base_url
        self.playwright = playwright
        self.browser = None


    async def setup(self):
        self.browser = await self.playwright.chromium.launch(headless=False)


    async def teardown(self):
        if self.browser:
            await self.browser.close()


    async def extract(self):
        logger.info(f"Iniciando extração de: {self.__class__.__name__}")
        await self.setup()
        all_ads = []
        try:
            page = await self.browser.new_page()
            logger.debug(f"Acessando URL: {self.base_url}")
            await page.goto(self.base_url,
                            timeout=60_000,
                            wait_until="domcontentloaded")
            await page.wait_for_timeout(2_000)     # 2 s
            ads = await self.get_ads(page)
            logger.info(f"{len(ads)} anúncios encontrados.")
            for idx, ad in enumerate(ads):
                try:
                    ad_data = await self.parse_ad(ad, page)
                    if ad_data:
                        (all_ads.extend(ad_data) if isinstance(ad_data, list)
                         else all_ads.append(ad_data))
                except Exception as e:
                    logger.warning(f"[{idx}] Falha ao extrair anúncio: {e}")
        except Exception as e:
            logger.error(f"Erro durante a extração: {e}")
        finally:
            await self.teardown()
            logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")
        return all_ads

    # Agora os filhos **também** têm que ser async:
    @abstractmethod
    async def get_ads(self, page):
        ...

    @abstractmethod
    async def parse_ad(self, ad, page):
        ...
