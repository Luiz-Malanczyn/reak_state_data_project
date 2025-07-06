import asyncio
from playwright.async_api import async_playwright
from pipeline.extract.olx_scraper import OlxScraper
from pipeline.extract.vivareal_scraper import VivaRealScraper
from pipeline.extract.chavesnamao_scraper import ChavesNaMaoScraper
from pipeline.extract.imovelweb_scraper import ImovelWebScraper
from pipeline.extract.zapimoveis_scraper import ZapImoveisScraper

SEM = asyncio.Semaphore(2)

SCRAPER_CLS = [
    #OlxScraper,
    #VivaRealScraper,
    ChavesNaMaoScraper,
    #ImovelWebScraper,
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
                price_start=10_000,
                max_price=50_000,
                price_step=10_000
            )
            for cls in SCRAPER_CLS
        ]


        results = await asyncio.gather(*(s.extract() for s in scrapers))
        all_ads = [ad for group in results for ad in (group or [])]
        print(f"Total de anúncios: {len(all_ads)}")


if __name__ == "__main__":
    asyncio.run(main())
