from pipeline.extract.base_scraper import BaseScraper
import re

class ChavesNaMaoScraper(BaseScraper):
    def __init__(self, playwright, valMin=0, valMax=100000):
        super().__init__(f"https://www.chavesnamao.com.br/imoveis-residenciais-a-venda/pr-curitiba/?filtro=pmin%3A{valMin}%2Cpmax%3A{valMax}&pg=", playwright)


    async def get_ads(self, page):
        page_height = await page.evaluate("document.body.scrollHeight")
        current_height = 500
        while current_height + 3500 < page_height:
            await page.evaluate(f"window.scrollTo(0, {current_height})")
            await page.wait_for_timeout(1000)
            current_height += 500
        await page.wait_for_timeout(2000)

        cutoff_el = await page.query_selector(".style-module__dHpwYa__container")
        cutoff_top = None
        if cutoff_el:
            cutoff_top = await page.evaluate("(el) => el.offsetTop", cutoff_el)

        all_ads = await page.query_selector_all('div[data-template="list"].styles-module__saqrOW__card.card-module__1awNxG__card')

        if not cutoff_top:
            return all_ads

        filtered_ads = []
        for ad in all_ads:
            ad_top = await page.evaluate("(el) => el.offsetTop", ad)
            if ad_top < cutoff_top:
                filtered_ads.append(ad)
            else:
                break

        return filtered_ads


    async def parse_ad(self, ad, page):
        async def get_text(el):
            return (await el.inner_text()).strip() if el else ""

        titulo_el = await ad.query_selector("h2.styles-module__5TXV2W__heading2.styles-module__saqrOW__title.style-module__PkTDxW__contentTitle")
        titulo = await get_text(titulo_el) or "Título não encontrado"

        infos = await ad.query_selector('span.card-module__1awNxG__cardContent')

        preco = self._extract_val(await get_text(await infos.query_selector('b')), r"([\d\.,]+)") if infos else None
        cond = self._extract_val(await get_text(await infos.query_selector('span[aria-label=\"Condominio\"]')), r"R\$ ([\d\.,]+)") if infos else None
        iptu = self._extract_val(await get_text(await infos.query_selector('span[aria-label=\"IPTU\"]')), r"R\$ ([\d\.,]+)") if infos else None

        detalhes_container = await infos.query_selector("span.style-module__PkTDxW__list") if infos else None
        detalhes = await detalhes_container.query_selector_all("p.styles-module__5TXV2W__body2.undefined") if detalhes_container else []

        tamanho = quartos = banheiros = vagas = None

        for d in detalhes:
            title = await d.get_attribute('title') or ''
            text = await get_text(d)

            if "Área" in title:
                tamanho = self._parse_int(title)
            elif "Quarto" in title or "Quartos" in title:
                quartos = self._parse_int(title)
            elif "Banheiro" in title or "Banheiros" in title:
                banheiros = self._parse_int(title)
            elif "Garagem" in title or "Garagens" in title:
                vagas = self._parse_int(title)

        rua_el = await ad.query_selector('p[title*=","]')
        rua = await get_text(rua_el) if rua_el else ""

        bairro_el = await ad.query_selector_all('p[title]')
        bairro = await get_text(bairro_el[1]) if len(bairro_el) > 1 else ""

        localizacao = f"{bairro}, {rua}" if bairro and rua else bairro or rua

        url_el = await ad.query_selector("a")
        href = await url_el.get_attribute("href") if url_el else None
        url = "https://www.chavesnamao.com.br" + href if href else None

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
    
    async def should_continue(self, page):
        elemento = await page.query_selector(".style-module__dHpwYa__container")
        if elemento:
            return False
        return True
