import asyncio
from playwright.async_api import async_playwright
from pipeline.extract.olx_scraper import OlxScraper
from pipeline.extract.vivareal_scraper import VivaRealScraper
from pipeline.extract.chavesnamao_scraper import ChavesNaMaoScraper
from pipeline.extract.imovelweb_scraper import ImovelWebScraper
from pipeline.extract.zapimoveis_scraper import ZapImoveisScraper

# Limita concorrência (útil se o PC não aguenta abrir 5 browsers de uma vez)
SEM = asyncio.Semaphore(2)

# Lista de scrapers a rodar
SCRAPER_CLS = [
    OlxScraper,
    VivaRealScraper,
    ChavesNaMaoScraper,
    ImovelWebScraper,
    ZapImoveisScraper,
]

# Função que roda um scraper isoladamente
async def run_scraper(scraper_cls, playwright):
    async with SEM:
        scraper = scraper_cls(playwright=playwright)
        return await scraper.extract()

# Função principal que coordena tudo
async def main():
    async with async_playwright() as playwright:
        scrapers = [
            # OlxScraper(playwright),
            # VivaRealScraper(playwright),
            ChavesNaMaoScraper(playwright),
            # ImovelWebScraper(playwright),
            # ZapImoveisScraper(playwright),
        ]

        results = await asyncio.gather(*(s.extract() for s in scrapers))
        all_ads = [ad for group in results for ad in (group or [])]
        print(f"Total de anúncios: {len(all_ads)}")


if __name__ == "__main__":
    asyncio.run(main())
