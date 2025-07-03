from pipeline.extract.base_scraper import BaseScraper
import re

class OlxScraper(BaseScraper):
    def __init__(self, playwright):
        super().__init__("https://www.olx.com.br/imoveis/venda/estado-pr/regiao-de-curitiba-e-paranagua/grande-curitiba", playwright)

    async def get_ads(self, page):
        return await page.query_selector_all('.olx-adcard__content[data-mode="horizontal"]')

    async def parse_ad(self, ad, page):
        async def get_text(selector):
            el = await ad.query_selector(selector)
            return (await el.inner_text()).strip() if el else ""

        titulo = await get_text("h2.olx-text.olx-text--body-large")

        preco_raw = await get_text(".olx-adcard__mediumbody")
        preco = self._extract_val(preco_raw, r"R\$ ([\d\.,]+)")
        iptu = self._extract_val(preco_raw, r"IPTU R\$ ([\d\.,]+)")
        condominio = self._extract_val(preco_raw, r"Condomínio R\$ ([\d\.,]+)")

        detalhes_raw = await get_text(".olx-adcard__detalhes")
        detalhes = detalhes_raw.split("\n") if detalhes_raw else []

        quartos = self._parse_int(detalhes[0]) if len(detalhes) > 0 else None
        tamanho = self._parse_int(detalhes[1]) if len(detalhes) > 1 else None
        vagas = self._parse_int(detalhes[2]) if len(detalhes) > 2 else None
        banheiros = self._parse_int(detalhes[3]) if len(detalhes) > 3 else None

        localizacao = await get_text(".olx-adcard__location")
        date = await get_text(".olx-adcard__date")

        url_el = await ad.query_selector("a.olx-adcard__link")
        url = await url_el.get_attribute("href") if url_el else None

        return {
            "titulo": titulo,
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
        }

    def _parse_int(self, text):
        if not text:
            return None
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _extract_val(self, raw_text, pattern):
        match = re.search(pattern, raw_text)
        return match.group(1).strip() if match else None
