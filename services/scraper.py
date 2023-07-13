import asyncio

import aiohttp
import requests
from bs4 import BeautifulSoup


page_size = 1000
url = f"https://auto.ria.com/uk/search/?indexName=order_auto&categories.main.id=1&brand.id[0]=79&model.id[0]=2104&abroad.not=1&custom.not=0&damage.not=0&country.import.usa.not=0&page=0&size={page_size}"  # noqa: E501

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36"
}
num_pictures = 5


def get_all_post_links() -> list[str]:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    search_results = soup.find(id="searchResults")
    links = search_results.select("div.item.ticket-title > a")
    return [link.get("href") for link in links]


async def get_page(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    async with session.get(url) as response:
        return url, await response.text()


async def get_all_pages(urls: list[str]):
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(get_page(session, url)))
        return await asyncio.gather(*tasks)


# def clean_price(price: str) -> float:
#     return float("".join([i for i in price if i.isdigit()]))


def parse(pages: tuple[str, str]) -> list[dict[str, str | list]]:
    cars = []
    for url, html in pages:
        soup = BeautifulSoup(html, "html.parser")
        name = soup.find("h1", class_="head").get("title")
        price = soup.find("div", class_="price_value").text.strip()
        photos_block = soup.select("div.preview-gallery.mhide")[0]
        images = [img.get("src") for img in photos_block.select("picture > img")[:num_pictures]]
        cars.append({"url": url, "name": name, "price": price, "images": images})
    return cars


def extract() -> tuple[list, list[dict[str, str | list]]]:
    links = get_all_post_links()
    pages = asyncio.run(get_all_pages(links))
    cars = parse(pages)
    return links, cars


if __name__ == "__main__":
    _, cars = extract()
    print(cars)
    print(len(cars))
