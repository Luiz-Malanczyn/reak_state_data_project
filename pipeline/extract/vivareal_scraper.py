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

        ads = page.query_selector_all('[data-cy="rp-property-cd"]')
        logger.info(f"Total de anúncios encontrados: {len(ads)}")
        for index, ad in enumerate(ads):
            try:
                preco_container = ad.query_selector('[data-cy="rp-cardProperty-price-txt"]')
                preco_raw = preco_container.inner_text().strip() if preco_container else ""

                preco_match = re.search(r"R\$ [\d\.\,]+", preco_raw)
                iptu_match = re.search(r"IPTU R\$ [\d\.\,]+", preco_raw)
                condominio_match = re.search(r"(Cond\.|Condom[ií]nio) R\$ [\d\.\,]+", preco_raw)

                preco = preco_match.group().split("R$")[-1].strip() if preco_match else None
                iptu = iptu_match.group().split("R$")[-1].strip() if iptu_match else None
                condominio = condominio_match.group().split("R$")[-1].strip() if condominio_match else None

                tamanho_element = ad.query_selector('[data-cy="rp-cardProperty-propertyArea-txt"]')
                quartos_element = ad.query_selector('[data-cy="rp-cardProperty-bedroomQuantity-txt"]')
                banheiros_element = ad.query_selector('[data-cy="rp-cardProperty-bathroomQuantity-txt"]')
                vagas_element = ad.query_selector('[data-cy="rp-cardProperty-parkingSpacesQuantity-txt"]')

                tamanho_raw = tamanho_element.inner_text().strip() if tamanho_element else None
                quartos_raw = quartos_element.inner_text().strip() if quartos_element else None
                banheiros_raw = banheiros_element.inner_text().strip() if banheiros_element else None
                vagas_raw = vagas_element.inner_text().strip() if vagas_element else None

                tamanho = int(re.search(r"\d+", tamanho_raw).group()) if tamanho_raw and re.search(r"\d+", tamanho_raw) else None
                quartos = int(re.search(r"\d+", quartos_raw).group()) if quartos_raw and re.search(r"\d+", quartos_raw) else None
                banheiros = int(re.search(r"\d+", banheiros_raw).group()) if banheiros_raw and re.search(r"\d+", banheiros_raw) else None
                vagas = int(re.search(r"\d+", vagas_raw).group()) if vagas_raw and re.search(r"\d+", vagas_raw) else None

                bairro_element = ad.query_selector('[data-cy="rp-cardProperty-location-txt"]')
                rua_element = ad.query_selector('[data-cy="rp-cardProperty-street-txt"]')

                bairro_raw = bairro_element.inner_text().strip() if bairro_element else ""
                rua_raw = rua_element.inner_text().strip() if rua_element else ""

                bairro_match = re.search(r"em\s+(.*)", bairro_raw)
                bairro = bairro_match.group(1).strip() if bairro_match else bairro_raw

                localizacao = f"{bairro}, {rua_raw}" if bairro and rua_raw else bairro or rua_raw

                date = "Data não encontrada"

                url_element = ad.query_selector("a")
                url = url_element.get_attribute("href") if url_element else "URL não encontrada"

                # logger.debug(f"[{index}] Anúncio extraído: Casa para comprar em {bairro} | {preco} | {quartos} | {tamanho} | {vagas} | {banheiros} | {localizacao} | {date} | {url}")

                all_ads.append({
                    "titulo": f"Casa para comprar em {bairro}",
                    "preco": preco,
                    "iptu": iptu,
                    "condominio": condominio,
                    "quartos": quartos,
                    "tamanho": tamanho,
                    "vagas": vagas,
                    "banheiros": banheiros,
                    "localizacao": localizacao,
                    "date": date,
                    "url": url
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