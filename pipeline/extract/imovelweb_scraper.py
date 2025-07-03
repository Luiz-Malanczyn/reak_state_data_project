from pipeline.extract.base_scraper import BaseScraper
import re

class ImovelWebScraper(BaseScraper):
    def __init__(self, playwright):
        super().__init__("https://www.imovelweb.com.br/casas-venda-curitiba-pr.html", playwright)

    async def get_ads(self, page):
        return await page.query_selector_all('div.postingsList-module__card-container')

    async def parse_ad(self, ad, page):
        async def get_text(selector):
            el = await ad.query_selector(selector)
            return (await el.inner_text()).strip() if el else ""

        preco = self._extract_val(await get_text('div.postingPrices-module__price'), r"R\$ ([\d\.,]+)")
        condominio = self._extract_val(await get_text('div[data-qa="expensas"]'), r"R\$ ([\d\.,]+)")

        features = await get_text('h3[data-qa="POSTING_CARD_FEATURES"]')

        tamanho = self._extract_val(features, r"(\d+)\s?m²")
        quartos = self._extract_val(features, r"(\d+)\s+quartos?")
        banheiros = self._extract_val(features, r"(\d+)\s+ban")
        vagas = self._extract_val(features, r"(\d+)\s+vagas?")

        tamanho = int(tamanho) if tamanho else None
        quartos = int(quartos) if quartos else None
        banheiros = int(banheiros) if banheiros else None
        vagas = int(vagas) if vagas else None

        rua = await get_text('.postingLocations-module__location-address-in-listing')
        bairro = await get_text('[data-qa="POSTING_CARD_LOCATION"]')
        localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

        url_el = await ad.query_selector("a")
        href = await url_el.get_attribute("href") if url_el else None
        url = "https://www.imovelweb.com.br/" + href if href else None

        descricao = (await url_el.inner_text()).strip() if url_el else ""
        titulo = f"Casa para comprar em {bairro}"

        return {
            "titulo": titulo,
            "preco": preco,
            "iptu": None,  # Não está presente
            "condominio": condominio,
            "quartos": quartos,
            "tamanho": tamanho,
            "vagas": vagas,
            "banheiros": banheiros,
            "localizacao": localizacao,
            "date": "Data não encontrada",
            "url": url,
            "descricao": descricao
        }

    def _extract_val(self, text, pattern):
        if not text:
            return None
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).replace('.', '').replace(',', '.') if match else None
