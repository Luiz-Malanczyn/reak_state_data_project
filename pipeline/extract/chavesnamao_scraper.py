from pipeline.extract.base_scraper import BaseScraper
import re

class ChavesNaMaoScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.chavesnamao.com.br/imoveis-a-venda/pr-curitiba/")

    def get_ads(self, page):
        # Scroll manual pra carregar tudo
        page_height = page.evaluate("document.body.scrollHeight")
        current_height = 500

        while current_height + 3500 < page_height:
            page.evaluate(f"window.scrollTo(0, {current_height})")
            page.wait_for_timeout(1000)
            current_height += 500

        page.wait_for_timeout(2000)
        return page.query_selector_all('div[data-template="list"].styles-module__ViVk2q__card.card-module__cvK-Xa__card')

    def parse_ad(self, ad, page):
        def get_text(el):
            return el.inner_text().strip() if el else ""

        titulo_el = ad.query_selector("h2.olx-text.olx-text--body-large")
        titulo = get_text(titulo_el) or "Título não encontrado"

        infos = ad.query_selector('span.card-module__cvK-Xa__cardContent')

        preco = self._extract_val(get_text(infos.query_selector('b')), r"([\d\.,]+)")
        cond = self._extract_val(get_text(infos.query_selector('small[aria-label="Condominio"]')), r"R\$ ([\d\.,]+)")
        iptu = self._extract_val(get_text(infos.query_selector('small[aria-label="IPTU"]')), r"R\$ ([\d\.,]+)")

        detalhes_container = infos.query_selector("span.style-module__Yo5w-q__list ")
        detalhes = detalhes_container.query_selector_all("p.styles-module__aBT18q__body2") if detalhes_container else []

        tamanho = quartos = banheiros = vagas = None

        for d in detalhes:
            text = get_text(d)
            if "m²" in text:
                tamanho = self._parse_int(text)
            elif "Quarto" in text:
                quartos = self._parse_int(text)
            elif "Banheiro" in text:
                banheiros = self._parse_int(text)
            elif "Garagem" in text:
                vagas = self._parse_int(text)

        rua = get_text(ad.query_selector('p[title*=","]'))
        bairro_el = ad.query_selector_all('p[title]')
        bairro = get_text(bairro_el[1]) if len(bairro_el) > 1 else ""

        localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

        url_el = ad.query_selector("a")
        url = "https://www.chavesnamao.com.br" + url_el.get_attribute("href") if url_el else None

        return {
            "titulo": f"Casa para comprar em {bairro}",
            "preco": preco,
            "iptu": iptu,
            "condominio": cond,
            "quartos": quartos,
            "tamanho": tamanho,
            "vagas": vagas,
            "banheiros": banheiros,
            "localizacao": localizacao,
            "date": "Data não encontrada",
            "url": url
        }

    def _parse_int(self, text):
        match = re.search(r"\d+", text)
        return int(match.group()) if match else None

    def _extract_val(self, text, pattern):
        match = re.search(pattern, text)
        return match.group(1).replace(".", "").replace(",", ".") if match else None
