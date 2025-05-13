from pipeline.extract.olx_scraper import extract_olx_ads
from pipeline.extract.vivareal_scraper import extract_vivareal_ads

if __name__ == "__main__":
    #ads = extract_olx_ads()
    ads = extract_vivareal_ads()
    for ad in ads:
        print(ad)
