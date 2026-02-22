import argparse
import asyncio
import math
import os
import random
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.place import Place


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://geo:geo_password@localhost:5433/geo_search",
)


CENTER_LAT = 64.5430
CENTER_LON = 40.5369


@dataclass
class SeedPlace:
    name: str
    category: Optional[str]
    brand: Optional[str]
    address: Optional[str]
    lat: float
    lon: float


def _geog_point(lon: float, lat: float) -> str:
    # PostGIS geography expects SRID=4326;POINT(lon lat)
    return f"SRID=4326;POINT({lon} {lat})"


def _meters_to_degrees_lat(meters: float) -> float:
    # Approximation is fine for small distances at city scale.
    return meters / 111_320.0


def _meters_to_degrees_lon(meters: float, lat: float) -> float:
    # Adjust for latitude to keep east-west jitter reasonable.
    return meters / (111_320.0 * max(0.1, abs(math.cos(math.radians(lat)))))


def _jitter_point(lat: float, lon: float, radius_m: float, rng: random.Random) -> tuple[float, float]:
    # Uniform-ish jitter inside a circle using polar coordinates.
    r = radius_m * (rng.random() ** 0.5)
    theta = rng.random() * 2.0 * math.pi
    d_lat = _meters_to_degrees_lat(r) * math.cos(theta)
    d_lon = _meters_to_degrees_lon(r, lat) * math.sin(theta)
    return lat + d_lat, lon + d_lon


def base_places() -> List[SeedPlace]:
    return [
        SeedPlace(
            name="Титан-Арена",
            category="арена",
            brand="Титан-Арена",
            address="Троицкий проспект, 20",
            lat=64.5423,
            lon=40.5363,
        ),
        SeedPlace(
            name="Чемпион Зоомаркет",
            category="зоомагазин",
            brand="Чемпион",
            address="Воскресенская ул., 7",
            lat=64.5442,
            lon=40.5359,
        ),
        SeedPlace(
            name="Аптека на Троицком",
            category="аптека",
            brand=None,
            address="Троицкий проспект, 35",
            lat=64.5426,
            lon=40.5386,
        ),
        SeedPlace(
            name="Аптека Север",
            category="аптека",
            brand=None,
            address="Троицкий проспект, 10",
            lat=64.5436,
            lon=40.5351,
        ),
        SeedPlace(
            name="Магнит",
            category="продукты",
            brand="Магнит",
            address="Набережная Северной Двины, 30",
            lat=64.5419,
            lon=40.5379,
        ),
        SeedPlace(
            name="Пятёрочка",
            category="продукты",
            brand="Пятёрочка",
            address="Воскресенская ул., 16",
            lat=64.5439,
            lon=40.5384,
        ),
        SeedPlace(
            name="Булочная №1",
            category="кондитерская",
            brand=None,
            address="Воскресенская ул., 12",
            lat=64.5444,
            lon=40.5372,
        ),
        SeedPlace(
            name="Кондитерская Сластёна",
            category="кондитерская",
            brand=None,
            address="Троицкий проспект, 28",
            lat=64.5427,
            lon=40.5356,
        ),
        SeedPlace(
            name="Зоомир",
            category="зоомагазин",
            brand=None,
            address="Набережная Северной Двины, 22",
            lat=64.5421,
            lon=40.5348,
        ),
        SeedPlace(
            name="Аптека Рядом",
            category="аптека",
            brand=None,
            address="Воскресенская ул., 3",
            lat=64.5440,
            lon=40.5352,
        ),
    ]


def generate_random_places(count: int, seed: int) -> List[SeedPlace]:
    rng = random.Random(seed)
    categories = [
        ("аптека", None),
        ("продукты", "Магнит"),
        ("продукты", "Пятёрочка"),
        ("кондитерская", None),
        ("зоомагазин", "Чемпион"),
        ("зоомагазин", None),
    ]

    streets = [
        "Троицкий проспект",
        "Воскресенская ул.",
        "Набережная Северной Двины",
        "Поморская ул.",
        "Ломоносова проспект",
    ]

    places: List[SeedPlace] = []
    for i in range(count):
        category, brand = rng.choice(categories)
        street = rng.choice(streets)
        house = rng.randint(1, 50)
        lat, lon = _jitter_point(CENTER_LAT, CENTER_LON, radius_m=420, rng=rng)
        name_base = {
            "аптека": "Аптека",
            "продукты": "Магазин",
            "кондитерская": "Кондитерская",
            "зоомагазин": "Зоомагазин",
        }.get(category, "Место")
        name = f"{name_base} {i + 1}"
        if brand:
            name = f"{brand} {i + 1}"

        places.append(
            SeedPlace(
                name=name,
                category=category,
                brand=brand,
                address=f"{street}, {house}",
                lat=lat,
                lon=lon,
            )
        )
    return places


async def seed(reset: bool, random_count: int, seed_value: int) -> int:
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    base = base_places()
    random_places = generate_random_places(random_count, seed_value)
    all_places = base + random_places

    async with Session() as session:
        if reset:
            await session.execute(delete(Place))
            await session.commit()

        session.add_all(
            [
                Place(
                    name=p.name,
                    category=p.category,
                    brand=p.brand,
                    address=p.address,
                    geog=_geog_point(p.lon, p.lat),
                    source="seed",
                )
                for p in all_places
            ]
        )
        await session.commit()

    await engine.dispose()
    return len(all_places)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed places around central Archangelsk.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing places before inserting.",
    )
    parser.add_argument(
        "--random-count",
        type=int,
        default=20,
        help="Number of additional random places to generate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic output.",
    )
    args = parser.parse_args()

    inserted = asyncio.run(seed(args.reset, args.random_count, args.seed))
    print(f"Inserted {inserted} places.")


if __name__ == "__main__":
    main()
