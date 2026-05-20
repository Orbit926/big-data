# Hotel Search Engine API

This document describes the API to search and filter hotels loaded from the local JSON data source.

## Endpoint

`GET /api/search/hotels/`

## Parameters

| Parameter | Description | Example |
|---|---|---|
| `q` | General textual search across name, description, city, country, amenities, and tags. | `q=beach` |
| `city` | Filter by city name. | `city=Cancun` |
| `country` | Filter by country name. | `country=Mexico` |
| `amenity` | Filter by a specific amenity. | `amenity=spa` |
| `tag` | Filter by a specific tag. | `tag=luxury` |
| `min_rating` | Minimum rating (inclusive). | `min_rating=4.5` |
| `page` | Pagination page number. | `page=2` |

## Example Requests

### General search
```http
GET /api/search/hotels/?q=luxury
```

### Multiple Filters
```http
GET /api/search/hotels/?q=beach&city=Cancun&min_rating=4.0&page=1
```

## Pagination & JSON Response

Results are paginated in groups of 10. The response contains the standard DRF pagination metadata (`count`, `next`, `previous`, `results`).

### Example Response
```json
{
  "count": 248,
  "next": "http://localhost:8000/api/search/hotels/?q=beach&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Hotel Solia Resort",
      "city": "Cancun",
      "country": "Mexico",
      "rating": 4.8,
      "reviews": 1324,
      "price_per_night": 220,
      "currency": "USD",
      "description": "Luxury beachfront hotel with spa and ocean view.",
      "amenities": [
        "wifi",
        "pool",
        "spa"
      ],
      "tags": [
        "luxury",
        "beach"
      ],
      "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945",
      "available": true
    }
  ]
}
```

## Possible Errors
- Providing an invalid `page` (e.g., beyond the total number of pages) returns a `404 Not Found`.
- Providing non-numeric data for `page` returns a `404 Not Found`.
