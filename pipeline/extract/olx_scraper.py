from pipeline.extract.base_scraper import BaseScraper
import re

class OlxScraper(BaseScraper):
    def __init__(
        self,
        playwright,
        *,
        iterate_price_ranges=False,
        price_start=0,
        price_step=10_000,
        max_price=1_000_000
    ):
        super().__init__(
            playwright,
            iterate_price_ranges=iterate_price_ranges,
            price_start=price_start,
            price_step=price_step,
            max_price=max_price
        )

    def build_url(self, page_number, valMin=None, valMax=None):
        filtro = ""
        if valMin is not None and valMax is not None:
            filtro = f"?ps={valMin}&pe={valMax}"
        return f"https://www.olx.com.br/imoveis/venda/estado-pr/regiao-de-curitiba-e-paranagua/grande-curitiba{filtro}&o={page_number}"

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

        detalhes_raw = await get_text(".olx-adcard__details")
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

    async def should_continue(self, page):
        elemento = await page.query_selector('.AdNotFound_wrapper__oSQnK')

        if elemento:
            return False
        return True