from util.browser import get_browser
from util.logger import logger
import re

BASE_URL = "https://www.vivareal.com.br/venda/parana/curitiba/?transacao=venda&onde=,Paran%C3%A1,Curitiba,,,,,city,BR%3EParana%3ENULL%3ECuritiba,-25.426899,-49.265198,"

def extract_vivareal_ads():
    all_ads = []
    logger.info("Iniciando extração da primeira página da VivaReal")
    browser, playwright = get_browser()
    try:
        page = browser.new_page()
        logger.debug(f"Acessando URL: {BASE_URL}")
        page.goto(BASE_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        ads = page.query_selector_all('[data-cy="rp-cardProperty-street-txt"]')
        logger.info(f"Total de anúncios encontrados: {len(ads)}")
        # for index, ad in enumerate(ads):
        #     try:
        #         titulo_element = ad.query_selector("h2.olx-text.olx-text--body-large")
        #         titulo = titulo_element.inner_text().strip() if titulo_element else "Título não encontrado"

        #         preco_element = ad.query_selector(".olx-adcard__mediumbody")
        #         preco_raw = preco_element.inner_text().strip() if preco_element else ""

        #         preco_match = re.search(r"R\$ [\d\.,]+(?=\\n|$)", preco_raw)
        #         iptu_match = re.search(r"IPTU R\$ [\d\.,]+(?=\\n|$)", preco_raw)
        #         condominio_match = re.search(r"Condomínio R\$ [\d\.,]+(?=\\n|$)", preco_raw)

        #         preco = preco_match.group().split("R$")[-1].strip() if preco_match else None
        #         iptu = iptu_match.group().split("R$")[-1].strip() if iptu_match else None
        #         condominio = condominio_match.group().split("R$")[-1].strip() if condominio_match else None

        #         detalhes_element = ad.query_selector(".olx-adcard__detalhes")
        #         detalhes_raw = detalhes_element.inner_text().strip() if detalhes_element else ""
        #         detalhes_split = detalhes_raw.split("\n")
        #         quartos = detalhes_split[0] if len(detalhes_split) > 0 else None
        #         tamanho = detalhes_split[1] if len(detalhes_split) > 1 else None
        #         vagas = detalhes_split[2] if len(detalhes_split) > 2 else None
        #         banheiros = detalhes_split[3] if len(detalhes_split) > 3 else None

        #         location_element = ad.query_selector(".olx-adcard__location")
        #         location = location_element.inner_text().strip() if location_element else "Local não encontrado"

        #         date_element = ad.query_selector(".olx-adcard__date")
        #         date = date_element.inner_text().strip() if date_element else "Data não encontrada"

        #         url_element = ad.query_selector("a.olx-adcard__link")
        #         url = url_element.get_attribute("href") if url_element else "URL não encontrada"

        #         # logger.debug(f"[{index}] Anúncio extraído: {titulo} | {preco} | {quartos} | {tamanho} | {vagas} | {banheiros} | {location} | {date} | {url}")

        #         all_ads.append({
        #             "titulo": titulo,
        #             "preco": preco,
        #             "iptu": iptu,
        #             "condominio": condominio,
        #             "quartos": quartos,
        #             "tamanho": tamanho,
        #             "vagas": vagas,
        #             "banheiros": banheiros,
        #             "location": location,
        #             "date": date,
        #             "url": url
        #         })
        #     except Exception as e:
        #         logger.warning(f"[{index}] Falha ao extrair anúncio: {e}")
    except Exception as e:
        logger.error(f"Erro durante a extração: {e}")
    finally:
        browser.close()
        playwright.stop()
        logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")
        return all_ads