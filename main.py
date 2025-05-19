from pipeline.extract.olx_scraper import OlxScraper
from pipeline.extract.vivareal_scraper import VivaRealScraper
from pipeline.extract.chavesnamao_scraper import ChavesNaMaoScraper
from pipeline.extract.imovelweb_scraper import ImovelWebScraper
from pipeline.extract.zapimoveis_scraper import ZapImoveisScraper

if __name__ == "__main__":
    scraper = ChavesNaMaoScraper()
    ads = scraper.extract()
    print(ads)