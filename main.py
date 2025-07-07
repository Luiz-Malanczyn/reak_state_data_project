import asyncio
from playwright.async_api import async_playwright
from pipeline.extract.olx_scraper import OlxScraper
from pipeline.extract.vivareal_scraper import VivaRealScraper
from pipeline.extract.chavesnamao_scraper import ChavesNaMaoScraper
from pipeline.extract.imovelweb_scraper import ImovelWebScraper
from pipeline.extract.zapimoveis_scraper import ZapImoveisScraper

SEM = asyncio.Semaphore(2)

SCRAPER_CLS = [
    OlxScraper,
    ChavesNaMaoScraper,
    #ImovelWebScraper,
    #VivaRealScraper,
    #ZapImoveisScraper,
]

async def run_scraper(scraper_cls, playwright):
    async with SEM:
        scraper = scraper_cls(playwright=playwright)
        return await scraper.extract()

async def main():
    async with async_playwright() as playwright:
        scrapers = [
            cls(
                playwright,
                iterate_price_ranges=True,
                price_start=120_000,
                max_price=2_000_000,
                price_step=10_000
            )
            for cls in SCRAPER_CLS
        ]

        results = await asyncio.gather(*(s.extract() for s in scrapers))
        total_ads = sum(results)
        print(f"Total de anúncios: {total_ads}")



if __name__ == "__main__":
    asyncio.run(main())
