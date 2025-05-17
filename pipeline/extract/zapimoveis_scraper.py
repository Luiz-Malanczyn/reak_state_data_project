from util.browser import get_browser
from util.logger import logger
import re

BASE_URL = "https://www.zapimoveis.com.br/venda/casas/pr+curitiba/"

def extract_zapimoveis_ads():
    all_ads = []
    def extrai_dados(ad, preco_extracted, url_extracted, multiple_ads=False):
        preco_container = ad.query_selector('[data-cy="rp-cardProperty-price-txt"]')
        preco_raw = preco_container.inner_text().strip() if preco_container else ""

        preco_match = re.search(r"R\$ [\d\.\,]+", preco_raw)
        iptu_match = re.search(r"IPTU R\$ [\d\.\,]+", preco_raw)
        condominio_match = re.search(r"(Cond\.|Condom[ií]nio) R\$ [\d\.\,]+", preco_raw)

        if multiple_ads:
            preco = preco_extracted
            url = url_extracted
        else:
            preco = preco_match.group().split("R$")[-1].strip() if preco_match else None
            url_element = ad.query_selector("a")
            url = url_element.get_attribute("href") if url_element else "URL não encontrada"
            
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

    logger.info("Iniciando extração da primeira página da ZapImoveis")
    browser, playwright = get_browser()
    try:
        page = browser.new_page()
        logger.debug(f"Acessando URL: {BASE_URL}")
        page.goto(BASE_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        print("Aguardando carregamento da página...")
        ads = page.query_selector_all('[data-cy="rp-property-cd"]')
        logger.info(f"Total de anúncios encontrados: {len(ads)}")
        for index, ad in enumerate(ads):
            try:
                botao = ad.query_selector('[data-cy="listing-card-deduplicated-button"]')
                if not botao:
                    extrai_dados(ad, None, None)
                else:
                    botao.click()
                    
                    page.wait_for_selector('[data-cy="deduplicated-modal"]', timeout=5000)
                    popup_section = page.query_selector('section.DeduplicationListings_card-listing__D17Um')
                    ads = popup_section.query_selector_all('a')
    
                    for ad in ads:
                        url = ad.get_attribute('href')

                        preco_element = ad.query_selector('h2.MainValue_advertiser__total__1ornY')
                        preco = preco_element.inner_text().strip() if preco_element else ""

                        extrai_dados(ad, preco, url, multiple_ads=True)
                    page.query_selector('span.l-drawer__close').click()
            except Exception as e:
                logger.warning(f"[{index}] Falha ao extrair anúncio: {e}")
    except Exception as e:
        logger.error(f"Erro durante a extração: {e}")
    finally:
        browser.close()
        playwright.stop()
        logger.success(f"Extração finalizada. Total de anúncios válidos: {len(all_ads)}")
        return all_ads