# Hotel Search Engine

This app implements a local hotel search engine, operating without a database.

## Data Source
The data is generated and stored in `data/hotels.json`.

## Core Logic
The application uses the `hotel_search.py` service to load data from JSON and apply search queries and filters locally.

## Endpoints
- `GET /api/search/hotels/`: Main endpoint with support for search (`q`), filters (`city`, `country`, `amenity`, `tag`), and pagination (`page`).
