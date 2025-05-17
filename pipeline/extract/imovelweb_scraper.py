from util.browser import get_browser
from util.logger import logger
import re

BASE_URL = "https://www.imovelweb.com.br/casas-venda-curitiba-pr.html"

def extract_imovelweb_ads():
    all_ads = []
    logger.info("Iniciando extração da primeira página da ImovelWeb")
    browser, playwright = get_browser()
    try:
        page = browser.new_page()
        logger.debug(f"Acessando URL: {BASE_URL}")
        page.goto(BASE_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        ads = page.query_selector_all('div.postingsList-module__card-container')
        logger.info(f"Total de anúncios encontrados: {len(ads)}")
        for index, ad in enumerate(ads):
            try:
                valores_container = ad.query_selector('div.postingPrices-module__posting-card-price-block')

                preco_raw = valores_container.query_selector('div.postingPrices-module__price')
                preco = preco_raw.inner_text().strip().split("R$")[-1].strip() if preco_raw else None
       
                condominio_raw = valores_container.query_selector('div[data-qa="expensas"]')
                condominio_text = condominio_raw.inner_text().strip() if condominio_raw else ""
                match = re.search(r"R\$ (\d[\d\.\,]*)", condominio_text)
                condominio = match.group(1).replace('.', '').replace(',', '.') if match else None

                features_h3 = ad.query_selector('h3[data-qa="POSTING_CARD_FEATURES"]')
                features_text = features_h3.inner_text().strip() if features_h3 else ""

                tamanho_match = re.search(r"(\d+)\s?m²", features_text)
                quartos_match = re.search(r"(\d+)\s+quartos?", features_text, re.IGNORECASE)
                banheiros_match = re.search(r"(\d+)\s+ban", features_text, re.IGNORECASE)
                vagas_match = re.search(r"(\d+)\s+vagas?", features_text, re.IGNORECASE)

                tamanho = int(tamanho_match.group(1)) if tamanho_match else None
                quartos = int(quartos_match.group(1)) if quartos_match else None
                banheiros = int(banheiros_match.group(1)) if banheiros_match else None
                vagas = int(vagas_match.group(1)) if vagas_match else None

                rua_element = ad.query_selector('.postingLocations-module__location-address-in-listing')
                bairro_element = ad.query_selector('[data-qa="POSTING_CARD_LOCATION"]')

                rua = rua_element.inner_text().strip() if rua_element else ""
                bairro = bairro_element.inner_text().strip() if bairro_element else ""

                localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

                date = "Data não encontrada"

                url_element = ad.query_selector("a")
                url = "https://www.imovelweb.com.br/" + url_element.get_attribute("href") if url_element else "URL não encontrada"

                descricao = url_element.inner_text().strip()

                all_ads.append({
                    "titulo": f"Casa para comprar em {bairro}",
                    "preco": preco,
                    "iptu": None,
                    "condominio": condominio,
                    "quartos": quartos,
                    "tamanho": tamanho,
                    "vagas": vagas,
                    "banheiros": banheiros,
                    "localizacao": localizacao,
                    "date": date,
                    "url": url,
                    "descricao": descricao
                })
            except Exception as e:
                logger.warning(f"[{index}] Falha ao extrair anúncio: {e}")
    except Exception as e:
        logger.error(f"Erro durante a extração: {e}")
    finally:
        browser.close()
        playwright.stop()
        logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")
        return all_ads