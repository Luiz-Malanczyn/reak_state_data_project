from abc import ABC, abstractmethod
from util.logger import logger


class BaseScraper(ABC):
    def __init__(self, base_url: str, playwright):
        self.base_url = base_url
        self.playwright = playwright
        self.browser = None
        self.logger = logger.bind(classname=self.__class__.__name__)


    async def setup(self):
        self.browser = await self.playwright.chromium.launch(headless=False)


    async def teardown(self):
        if self.browser:
            await self.browser.close()


    async def should_continue(self, page):
        return True


    async def extract(self):
        self.logger.info(f"Iniciando extração de: {self.__class__.__name__}")
        await self.setup()
        all_ads = []
        page_number = 1

        try:
            page = await self.browser.new_page()

            while True:
                if not await self.should_continue(page):
                    self.logger.info(f"Condição de parada customizada atendida na página {page_number}. Encerrando.")
                    break

                url = f"{self.base_url}{page_number}"
                self.logger.debug(f"Acessando URL: {url}")
                await page.goto(url, timeout=60_000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2_000)

                ads = await self.get_ads(page)
                if not ads:
                    self.logger.info(f"Nenhum anúncio encontrado na página {page_number}. Encerrando.")
                    break

                self.logger.info(f"{len(ads)} anúncios encontrados na página {page_number}.")

                for idx, ad in enumerate(ads):
                    try:
                        ad_data = await self.parse_ad(ad, page)
                        if ad_data:
                            (all_ads.extend(ad_data) if isinstance(ad_data, list)
                            else all_ads.append(ad_data))
                    except Exception as e:
                        self.logger.warning(f"[{idx}] Falha ao extrair anúncio: {e}")

                page_number += 1

        except Exception as e:
            self.logger.error(f"Erro durante a extração: {e}")
        finally:
            await self.teardown()
            self.logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")

        return all_ads


    @abstractmethod
    async def get_ads(self, page):
        ...

    @abstractmethod
    async def parse_ad(self, ad, page):
        ...
