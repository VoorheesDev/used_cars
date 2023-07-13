import time

import schedule

from db import database, models
from services import posting, scraper


caption_template = "*{name}*\n[Look at auto\.ria]({url})\n*{price}*"  # noqa: W605


def find_shared_and_unique_urls(site_urls: list[str], db_urls: list[str]) -> tuple[list[str], ...]:
    shared_urls = list(set(site_urls) & set(db_urls))
    unique_site_urls = [url for url in site_urls if url not in shared_urls]
    unique_db_urls = [url for url in db_urls if url not in shared_urls]

    return shared_urls, unique_site_urls, unique_db_urls


def sync_prices(cars: list[dict[str, str | list]]) -> None:
    for car in cars:
        new_price = car["price"]
        car_in_db = database.get_car_by_url(car["url"])
        old_price = car_in_db.price
        if new_price != old_price:
            caption = caption_template.format(
                name=car_in_db.name,
                url=car_in_db.url,
                price=f"~{old_price}~ {new_price}",
            )
            posting.update_post(car_in_db.post_id, caption, "The price has been changed")
            database.update_price_by_url(car["url"], new_price)


def create_new_posts(cars: list[dict[str, str | int | list]]) -> None:
    for car in cars:
        caption = caption_template.format(name=car["name"], url=car["url"], price=car["price"])
        post_id = posting.create_post(car["images"], caption)
        car.update(post_id=post_id)
    database.insert_cars(cars)


def delete_obsolete_posts(cars: list[models.Car]) -> None:
    for car in cars:
        caption = f"*SOLD*\n~{car.name}\n{car.price}~"
        posting.update_post(car.post_id, caption, "The car has been sold")
        database.delete_car_by_url(car.url)


def main():
    database.create_db_and_tables()

    site_urls, site_cars = scraper.extract()
    db_urls = database.get_all_urls()

    shared_urls, unique_site_urls, unique_db_urls = find_shared_and_unique_urls(site_urls, db_urls)
    shared_cars = [car for car in site_cars if car["url"] in shared_urls]
    unique_site_cars = [car for car in site_cars if car["url"] in unique_site_urls]
    unique_db_cars = [database.get_car_by_url(url) for url in unique_db_urls]

    sync_prices(shared_cars)
    create_new_posts(unique_site_cars)
    delete_obsolete_posts(unique_db_cars)


if __name__ == "__main__":
    schedule.every(10).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
