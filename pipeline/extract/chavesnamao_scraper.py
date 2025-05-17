from util.browser import get_browser
from util.logger import logger
import re

BASE_URL = "https://www.chavesnamao.com.br/imoveis-a-venda/pr-curitiba/"

def extract_chavesnamao_ads():
    all_ads = []
    logger.info("Iniciando extração da primeira página da Chaves na Mão")
    browser, playwright = get_browser()
    try:
        page = browser.new_page()
        logger.debug(f"Acessando URL: {BASE_URL}")
        page.goto(BASE_URL, timeout=60000, wait_until="domcontentloaded")

        page_height = page.evaluate("document.body.scrollHeight")
        current_height = 500

        while current_height + 3500 < page_height:
            page.evaluate(f"window.scrollTo(0, {current_height})")
            page.wait_for_timeout(1000)
            current_height = current_height + 500

        page.wait_for_timeout(2000)

        ads = page.query_selector_all('div[data-template="list"].styles-module__ViVk2q__card.card-module__cvK-Xa__card')
        logger.info(f"Total de anúncios encontrados: {len(ads)}")
        for index, ad in enumerate(ads):
            try:
                titulo_element = ad.query_selector("h2.olx-text.olx-text--body-large")
                titulo = titulo_element.inner_text().strip() if titulo_element else "Título não encontrado"

                infos_container = ad.query_selector('span.card-module__cvK-Xa__cardContent')

                preco_raw = infos_container.query_selector('b')
                preco = preco_raw.inner_text().strip().split("R$")[-1].strip() if preco_raw else None

                condominio_raw = infos_container.query_selector('small[aria-label="Condominio"]')
                condominio_text = condominio_raw.inner_text().strip() if condominio_raw else ""
                condominio_match = re.search(r"R\$ [\d\.\,]+", condominio_text)
                condominio = condominio_match.group().split("R$")[-1].strip() if condominio_match else None

                iptu_raw = infos_container.query_selector('small[aria-label="IPTU"]')
                iptu_text = iptu_raw.inner_text().strip() if iptu_raw else ""
                iptu_match = re.search(r"R\$ [\d\.\,]+", iptu_text)
                iptu = iptu_match.group().split("R$")[-1].strip() if iptu_match else None

                detalhes_container = infos_container.query_selector("span.style-module__Yo5w-q__list ")
                detales_list_container = detalhes_container.query_selector_all("p.styles-module__aBT18q__body2")

                tamanho = None
                quartos = None
                vagas = None
                banheiros = None

                for detalhe in detales_list_container:
                    text = detalhe.inner_text().strip()

                    tamanho_match = re.search(r"(\d+)\s?m²", text)
                    quartos_match = re.search(r"(\d+)\s*Quartos?", text, re.IGNORECASE)
                    vagas_match = re.search(r"(\d+)\s*Garagem", text, re.IGNORECASE)
                    banheiros_match = re.search(r"(\d+)\s*Banheiros?", text, re.IGNORECASE)

                    if tamanho_match: tamanho = int(tamanho_match.group(1)); continue
                    if quartos_match: quartos = int(quartos_match.group(1)); continue
                    if vagas_match: vagas = int(vagas_match.group(1)); continue
                    if banheiros_match: banheiros = int(banheiros_match.group(1)); continue

                rua_element = ad.query_selector('p[title*=","]')
                bairro_element = ad.query_selector_all('p[title]')[1]

                rua = rua_element.inner_text().strip() if rua_element else ""
                bairro = bairro_element.inner_text().strip() if bairro_element else ""

                localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

                date = "Data não encontrada"

                url_element = ad.query_selector("a")
                url = "https://www.chavesnamao.com.br" + url_element.get_attribute("href") if url_element else "URL não encontrada"

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