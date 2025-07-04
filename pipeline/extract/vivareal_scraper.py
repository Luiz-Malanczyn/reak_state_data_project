from pipeline.extract.base_scraper import BaseScraper
from util.logger import logger
import re

class VivaRealScraper(BaseScraper):
    def __init__(self, playwright):
        super().__init__("https://www.zapimoveis.com.br/venda/casas/pr+curitiba/", playwright)

    async def get_ads(self, page):
        return await page.query_selector_all('[data-cy="rp-property-cd"]')

    async def parse_ad(self, ad, page):
        async def extract_text(selector):
            element = await ad.query_selector(selector)
            return (await element.inner_text()).strip() if element else None

        preco_raw = await extract_text('[data-cy="rp-cardProperty-price-txt"]') or ""
        preco = self._extract_val(preco_raw, r"R\$ ([\d\.,]+)")
        iptu = self._extract_val(preco_raw, r"IPTU R\$ ([\d\.,]+)")
        condominio = self._extract_val(preco_raw, r"(?:Cond\.|Condom[ií]nio) R\$ ([\d\.,]+)")

        tamanho = self._parse_int(await extract_text('[data-cy="rp-cardProperty-propertyArea-txt"]'))
        quartos = self._parse_int(await extract_text('[data-cy="rp-cardProperty-bedroomQuantity-txt"]'))
        banheiros = self._parse_int(await extract_text('[data-cy="rp-cardProperty-bathroomQuantity-txt"]'))
        vagas = self._parse_int(await extract_text('[data-cy="rp-cardProperty-parkingSpacesQuantity-txt"]'))

        bairro_raw = await extract_text('[data-cy="rp-cardProperty-location-txt"]')
        rua = await extract_text('[data-cy="rp-cardProperty-street-txt"]')
        bairro = re.search(r"em\s+(.*)", bairro_raw).group(1) if bairro_raw and "em " in bairro_raw else bairro_raw
        localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

        botao = await ad.query_selector('[data-cy="listing-card-deduplicated-button"]')

        if not botao:
            url_el = await ad.query_selector("a")
            url = await url_el.get_attribute("href") if url_el else None
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

        try:
            await botao.click()
            await page.wait_for_timeout(5000)
            await page.wait_for_selector('[data-cy="deduplication-modal-list-step"]', timeout=10000)

            popup_section = await page.query_selector('section.DeduplicationListings_card-listing__D17Um')
            if not popup_section:
                return []

            ads_popup = await popup_section.query_selector_all('a')
            results = []

            for ad_popup in ads_popup:
                url = await ad_popup.get_attribute('href')
                preco_element = await ad_popup.query_selector('h2.MainValue_advertiser__total__1ornY')
                preco_popup = (await preco_element.inner_text()).strip() if preco_element else None

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

            await page.mouse.click(10, 10)
            await page.wait_for_timeout(1000)
            return results

        except Exception as e:
            self.logger.warning(f"Falha ao processar popup de deduplicação: {e}")
            return []

    def _parse_int(self, text):
        if not text:
            return None
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _extract_val(self, raw_text, pattern):
        match = re.search(pattern, raw_text)
        return match.group(1).strip() if match else None
