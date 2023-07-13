import sqlite3


conn = sqlite3.connect("database.db")
# setting to get a dict from sqlite query instead of tuple
conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
cursor = conn.cursor()


def create_db_and_tables():
    cursor.executescript(
        """CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        price TEXT NOT NULL,
                        post_id INTEGER
                    );
                    CREATE TABLE IF NOT EXISTS car_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        car_id INTEGER NOT NULL,
                        path TEXT UNIQUE NOT NULL,
                        FOREIGN KEY (car_id) REFERENCES cars (id)
                    );"""
    )


def insert_car(car: dict[str, str | list]) -> None:
    with conn:
        cursor.execute(
            "INSERT OR IGNORE INTO cars (url, name, price, post_id) VALUES (:url, :name, :price, :post_id)",  # noqa: E501
            car,
        )
        car_id = cursor.lastrowid
        for image_path in car.get("images", []):
            cursor.execute(
                "INSERT OR IGNORE INTO car_images (car_id, path) VALUES (?, ?)",
                (car_id, image_path),
            )


def insert_cars(cars: list[dict[str, str | list]]) -> None:
    for car in cars:
        insert_car(car)


def get_car_by_url(url: str) -> tuple[int | str]:
    cursor.execute("SELECT * FROM cars WHERE cars.url = ?", (url,))
    return cursor.fetchone()


def get_all_cars() -> list[tuple[int | str]]:
    cursor.execute("SELECT * FROM cars")
    return cursor.fetchall()


def update_car_price(url: str, price: str) -> None:
    with conn:
        cursor.execute("UPDATE cars SET price = ? WHERE url = ?", (price, url))


def delete_car_by_url(url: str) -> None:
    with conn:
        cursor.execute("SELECT id FROM cars WHERE url = ?", (url,))
        row = cursor.fetchone()
        if row:
            cursor.execute("DELETE FROM cars WHERE url = ?", (url,))
            cursor.execute("DELETE FROM car_images WHERE car_id = ?", (row["id"],))
