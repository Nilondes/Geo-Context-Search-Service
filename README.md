# Geo-Context-Search-Service

A backend service that finds up to 5 nearest geographic locations within a 500-meter radius based on a natural language search context.

## Key Features:

The service receives:

1. Coordinates of a location point in the format:

   latitude:longitude
   
  
3. A natural language search context, such as:

    "Buy cat food at Champion"

    "Go to Titan Arena"

    "Buy medicine at a pharmacy on Troitsky"

    "Buy groceries"

    "Order a cake"

Given the input point and search context, the service:

- Extracts meaningful search intent (category, brand name, street, etc.)

- Searches within a 500-meter radius

- Returns up to 5 nearest matching locations

- Sorts results by distance (ascending)

- Returns fewer than 5 results if applicable

- Returns an empty list if no matches are found

## Technology Stack

    - Python 3.11+

    - PostgreSQL
    
    - FastAPI

    - Pydantic

    - PostGIS

    - External GIS API (OpenStreetMap / Google Places / Yandex Maps)

    - Docker / Docker Compose

    - Pytest

## Project Structure

Geo-Context-Search-Service/

│

├── app/

│   ├── main.py                # FastAPI entrypoint

│   ├── api/

│   │   └── routes.py          # /search endpoint

│   │

│   ├── core/

│   │   ├── config.py          # Settings (env variables)

│   │   └── dependencies.py    # Dependency injection

│   │

│   ├── services/

│   │   ├── context_parser.py  # Natural language processing logic

│   │   └── geo_service.py     # Geospatial search logic

│   │

│   ├── repositories/

│   │   └── places_repository.py  # DB interaction layer

│   │

│   ├── models/

│   │   ├── schemas.py         # Pydantic models (request/response)

│   │   └── db_models.py       # SQLAlchemy models

│   │

│   └── utils/

│       └── distance.py        # Optional Haversine fallback

│

├── tests/

│   ├── test_context_parser.py

│   ├── test_geo_service.py

│   └── test_api.py

│

├── migrations/

│

├── docker-compose.yml

├── Dockerfile

├── requirements.txt

└── README.md

  ## API Design

POST /search

Request

    {
  
      "location": "64.5401:40.5433",
  
      "context": "Buy medicine at a pharmacy on Troitsky"
  
    }

Response

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

## Context Processing Strategy

The natural language input will be processed to extract:

- Business category (e.g., pharmacy, grocery, bakery)

- Specific brand name (e.g., "Champion")

- Location constraints (e.g., street name)

Possible approaches:

- Keyword-based mapping (MVP version)

- Rule-based intent extraction

- NLP models (optional enhancement)

## Getting started

```sh
git clone https://github.com/Nilondes/Geo-Context-Search-Service.git
cd Geo-Context-Search-Service
```

```sh
pip install -r requirements.txt
```

```sh
uvicorn app.main:app --reload
```

Service available at:

```sh
http://localhost:8000/docs
```
