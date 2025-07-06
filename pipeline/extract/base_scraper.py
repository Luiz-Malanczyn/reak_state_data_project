from abc import ABC, abstractmethod
from util.logger import logger


class BaseScraper(ABC):
    def __init__(
        self,
        playwright,
        *,
        iterate_price_ranges=False,
        price_start=0,
        price_step=10_000,
        max_price=1_000_000
    ):
        self.playwright = playwright
        self.iterate_price_ranges = iterate_price_ranges
        self.price_start = price_start
        self.price_step = price_step
        self.max_price = max_price
        self.browser = None
        self.logger = logger.bind(classname=self.__class__.__name__)

    async def setup(self):
        self.browser = await self.playwright.chromium.launch(headless=False)

    async def teardown(self):
        if self.browser:
            await self.browser.close()

    async def should_continue(self, page):
        return True

    @abstractmethod
    def build_url(self, page_number: int, valMin: int | None = None, valMax: int | None = None) -> str:
        ...

    async def extract(self):
        self.logger.info(f"Iniciando extração de: {self.__class__.__name__}")
        await self.setup()
        all_ads = []

        try:
            page = await self.browser.new_page()

            price_ranges = [(None, None)]
            if self.iterate_price_ranges:
                price_ranges = [
                    (valMin, valMin + self.price_step - 1)
                    for valMin in range(self.price_start, self.max_price, self.price_step)
                ]

            for valMin, valMax in price_ranges:
                page_number = 1
                while True:
                    url = self.build_url(page_number, valMin, valMax)
                    self.logger.debug(f"Acessando URL: {url}")
                    await page.goto(url, timeout=60_000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(60_000)

                    ads = await self.get_ads(page)
                    if not ads:
                        self.logger.info(f"Nenhum anúncio encontrado na página {page_number} (Faixa: {valMin}-{valMax}).")
                        break

                    self.logger.info(f"{len(ads)} anúncios encontrados na página {page_number} (Faixa: {valMin}-{valMax})")

                    for idx, ad in enumerate(ads):
                        try:
                            ad_data = await self.parse_ad(ad, page)
                            if ad_data:
                                (all_ads.extend(ad_data) if isinstance(ad_data, list)
                                 else all_ads.append(ad_data))
                        except Exception as e:
                            self.logger.warning(f"[{idx}] Falha ao extrair anúncio: {e}")

                    if not await self.should_continue(page):
                        self.logger.info(f"Condição de parada customizada atendida. Encerrando página atual.")
                        break

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
