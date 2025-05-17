from pipeline.extract.olx_scraper import extract_olx_ads
from pipeline.extract.vivareal_scraper import extract_vivareal_ads
from pipeline.extract.chavesnamao_scraper import extract_chavesnamao_ads
from pipeline.extract.imovelweb_scraper import extract_imovelweb_ads
from pipeline.extract.zapimoveis_scraper import extract_zapimoveis_ads

if __name__ == "__main__":
    #ads = extract_olx_ads()
    #ads = extract_vivareal_ads()
    #ads = extract_chavesnamao_ads()
    #ads = extract_imovelweb_ads()
    ads = extract_zapimoveis_ads()
    for ad in ads:
        print(ad)
