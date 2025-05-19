from pipeline.extract.base_scraper import BaseScraper
import re

class ZapImoveisScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.zapimoveis.com.br/venda/casas/pr+curitiba/")

    def get_ads(self, page):
        return page.query_selector_all('[data-cy="rp-property-cd"]')

    def parse_ad(self, ad, page):
        def extract_text(selector):
            element = ad.query_selector(selector)
            return element.inner_text().strip() if element else None

        preco_raw = extract_text('[data-cy="rp-cardProperty-price-txt"]') or ""
        preco = self._extract_val(preco_raw, r"R\$ ([\d\.,]+)")
        iptu = self._extract_val(preco_raw, r"IPTU R\$ ([\d\.,]+)")
        condominio = self._extract_val(preco_raw, r"(?:Cond\.|Condom[ií]nio) R\$ ([\d\.,]+)")

        tamanho = self._parse_int(extract_text('[data-cy="rp-cardProperty-propertyArea-txt"]'))
        quartos = self._parse_int(extract_text('[data-cy="rp-cardProperty-bedroomQuantity-txt"]'))
        banheiros = self._parse_int(extract_text('[data-cy="rp-cardProperty-bathroomQuantity-txt"]'))
        vagas = self._parse_int(extract_text('[data-cy="rp-cardProperty-parkingSpacesQuantity-txt"]'))

        bairro_raw = extract_text('[data-cy="rp-cardProperty-location-txt"]')
        rua = extract_text('[data-cy="rp-cardProperty-street-txt"]')
        bairro = re.search(r"em\s+(.*)", bairro_raw).group(1) if bairro_raw and "em " in bairro_raw else bairro_raw
        localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

        botao = ad.query_selector('[data-cy="listing-card-deduplicated-button"]')

        # Caso simples: sem popup
        if not botao:
            url = ad.query_selector("a").get_attribute("href") if ad.query_selector("a") else None
            return {
                "titulo": f"Casa para comprar em {bairro}",
                "preco": preco,
                "iptu": iptu,
                "condominio": condominio,
                "quartos": quartos,
                "tamanho": tamanho,
                "vagas": vagas,
                "banheiros": banheiros,
                "localizacao": localizacao,
                "date": "Data não encontrada",
                "url": url,
            }

        # Caso popup com múltiplos anúncios
        try:
            botao.click()
            page.wait_for_timeout(5000)
            page.wait_for_selector('[data-cy="deduplication-modal-list-step"]', timeout=10000)

            popup_section = page.query_selector('section.DeduplicationListings_card-listing__D17Um')
            if not popup_section:
                return []

            ads_popup = popup_section.query_selector_all('a')
            results = []

            for ad_popup in ads_popup:
                url = ad_popup.get_attribute('href')
                preco_element = ad_popup.query_selector('h2.MainValue_advertiser__total__1ornY')
                preco_popup = preco_element.inner_text().strip() if preco_element else None

                results.append({
                    "titulo": f"Casa para comprar em {bairro}",
                    "preco": preco_popup,
                    "iptu": iptu,
                    "condominio": condominio,
                    "quartos": quartos,
                    "tamanho": tamanho,
                    "vagas": vagas,
                    "banheiros": banheiros,
                    "localizacao": localizacao,
                    "date": "Data não encontrada",
                    "url": url,
                })

            # fecha o modal
            page.mouse.click(10, 10)
            page.wait_for_timeout(1000)
            return results

        except Exception as e:
            from util.logger import logger
            logger.warning(f"Falha ao processar popup de deduplicação: {e}")
            return []


    def _parse_int(self, text):
        if not text:
            return None
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _extract_val(self, raw_text, pattern):
        match = re.search(pattern, raw_text)
        return match.group(1).strip() if match else None
