import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("Scraper")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(name)s:%(levelname)s - %(message)s")


def get_phone(phone_div):
    sku = phone_div.get('data-sku')
    link_tag = phone_div.find('a', {'class': ["link"]})
    link = link_tag.get('href')
    img_tag = phone_div.find('img', {'class': ['lazy', 'image', '-loaded']})
    img_url = img_tag.get('data-src')
    brand = phone_div.find('span', {'class': ['brand']}).text
    name = phone_div.find('span', {'class': ['name']}).text
    price_container = phone_div.find('span', {'class': ['price']})
    price = price_container.find('span', {'dir': ['ltr']}).get('data-price')

    result, data = save_phone_to_db(brand=brand, image_url=img_url, name=name,
                                    price=price, sku=sku, link=link)

    return data


def save_phone_to_db(brand, image_url, name, price, sku, link):
    # todo finish saving to database
    data = {
        "brand": brand,
        "name": name,
        "sku": sku,
        "price": int(float(price)),
        "link": link,
        "image_url": image_url
    }
    response = requests.post('https://jumia-core.herokuapp.com/api/phones/add', data)
    logger.info(f"{data.get('name')} {data.get('brand')} {data.get('sku')} {response.status_code} ")
    return response.status_code, data


def start_scraping():
    page_link = "https://www.jumia.ug/smartphones/"
    response = requests.get(page_link)

    soup = BeautifulSoup(response.content, 'html.parser')

    phone_divs = soup.find_all('div', {"class": ["sku", '-gallery']})
    for phone in phone_divs:
        _ = get_phone(phone)

    pagination = soup.find('ul', {"class": "osh-pagination -horizontal"})
    max_page = max(
        [int(i.text) for i in pagination.find_all('li') if i.text.isnumeric()])

    pages_to_scrape = [f"{page_link}?page={i}" for i in range(2, max_page + 1)]

    for page in pages_to_scrape:
        response = requests.get(page)
        soup = BeautifulSoup(response.content, 'html.parser')
        phone_divs = soup.find_all('div', {"class": ["sku", '-gallery']})
        logger.info(f"Scraping {page} and {len(phone_divs)} phones found")
        for phone in phone_divs:
            _ = get_phone(phone)
