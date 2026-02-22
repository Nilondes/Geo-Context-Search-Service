# Geo-Context-Search-Service

A backend service that finds up to 5 nearest geographic locations within a 500-meter radius based on a natural language search context.

## Key Features

The service receives:

1. Coordinates in the format `latitude:longitude`
2. A natural language search context, such as:

"Buy cat food at Champion"

"Go to Titan Arena"

"Buy medicine at a pharmacy on Troitsky"

"Buy groceries"

"Order a cake"

Given the input point and search context, the service:

- Extracts structured intent (category, brand, street)
- Searches within a 500-meter radius
- Returns up to 5 nearest matching locations
- Sorts results by distance (ascending)
- Returns fewer than 5 results if applicable
- Returns an empty list if no matches are found

## Technology Stack

- Python 3.11+
- PostgreSQL
- PostGIS
- FastAPI
- Pydantic
- SQLAlchemy (async)
- Alembic
- Docker / Docker Compose
- Pytest

## Project Structure

```
Geo-Context-Search-Service/
├── app/
│   ├── api/
│   │   └── routes.py              # /search endpoint
│   ├── core/
│   │   ├── db.py                  # async DB session factory
│   │   └── env.py                 # minimal .env loader
│   ├── data/
│   │   ├── brands.json            # known brand names
│   │   └── categories.json        # category keyword map
│   ├── models/
│   │   ├── base.py                # SQLAlchemy base
│   │   ├── place.py               # Place model
│   │   └── schemas.py             # Pydantic request/response
│   ├── repositories/
│   │   └── places_repository.py   # geo queries
│   ├── services/
│   │   ├── context_parser.py      # text parsing logic
│   │   └── geo_service.py         # orchestration layer
│   └── main.py                    # FastAPI app
├── migrations/                    # Alembic migrations
├── scripts/
│   └── seed_places.py             # seed sample data
├── tests/
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## API Design

POST `/search`

Request

```
{
  "location": "64.5401:40.5433",
  "context": "Buy medicine at a pharmacy on Troitsky"
}
```

Response

```
{
  "results": [
    {
      "name": "Pharmacy #1",
      "latitude": 64.5405,
      "longitude": 40.5428,
      "distance_meters": 120
    }
  ]
}
```

## Context Processing Strategy

The natural language input is parsed to extract:

- Business category (e.g., pharmacy, grocery, bakery)
- Specific brand name (e.g., "Champion")
- Location constraints (e.g., street name)

Current approach:

- Keyword-based mapping with lemmatization
- Rule-based intent extraction

## Database Structure

Table: `places`

Columns:

- `id` (int, PK)
- `name` (text, required)
- `category` (varchar, indexed)
- `brand` (varchar, indexed)
- `address` (text, nullable)
- `geog` (geography POINT, SRID 4326)
- `source` (varchar, nullable)
- `metadata_json` (jsonb, nullable)
- `created_at` (timestamp with timezone, server default now)

Notes:

- Spatial queries use PostGIS `ST_DWithin` and `ST_Distance` on the `geog` column.
- Coordinates are stored as geography points to get meter-based distances.

## Getting Started

### 1) Configure environment

Create a local `.env` file (based on `.env.example`) and set connection details:

```
cp .env.example .env
```

Set values in `.env`:

```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=geo_search
DB_USER=geo
DB_PASSWORD=geo_password

TEST_DB_HOST=localhost
TEST_DB_PORT=5434
TEST_DB_NAME=test_db
TEST_DB_USER=postgres
TEST_DB_PASSWORD=postgres

DATABASE_URL=postgresql+asyncpg://geo:geo_password@localhost:5433/geo_search
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/test_db
```

### 2) Start Postgres + PostGIS with Docker

```
docker compose up -d
```

### 3) Run migrations

```
alembic upgrade head
```

### 4) Seed sample data (optional)

```
python scripts/seed_places.py
```

Script flags:

- `--reset` clears existing rows before inserting
- `--random-count N` adds N random places near the center point
- `--seed N` sets RNG seed for reproducible random data

Example:

```
python scripts/seed_places.py --reset --random-count 200 --seed 42
```

### 5) Run the API

```
uvicorn app.main:app --reload
```

Open:

```
http://localhost:8000/docs
```

### 6) Run tests

```
pytest -q
```

## Notes

- The app reads environment variables from `.env` using a lightweight loader in `app/core/env.py`.
- `alembic` uses `DATABASE_URL` and automatically switches to a sync driver if needed.
